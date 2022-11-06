import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as secretsmanager from "aws-cdk-lib/aws-secretsmanager";
import { Function, Runtime, Code, Tracing } from "aws-cdk-lib/aws-lambda";
import * as path from "path";
import { Effect, PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Duration } from "aws-cdk-lib";
import { Cors, LambdaIntegration, RestApi } from "aws-cdk-lib/aws-apigateway";
import { DnsValidatedCertificate } from "aws-cdk-lib/aws-certificatemanager";
import {
  ARecord,
  HostedZone,
  IHostedZone,
  RecordTarget,
} from "aws-cdk-lib/aws-route53";
import { ApiGateway } from "aws-cdk-lib/aws-route53-targets";

export class WillkronbergDevLambdaStack extends cdk.Stack {
  public readonly api: RestApi;
  private readonly hostedZone: IHostedZone;
  private readonly certificate: DnsValidatedCertificate;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const fn = new Function(this, "MainHandler", {
      runtime: Runtime.PYTHON_3_9,
      handler: "willkronberg.app.lambda_handler",
      code: Code.fromDockerBuild(path.join(__dirname, "..", "..")),
      timeout: Duration.seconds(30),
      tracing: Tracing.ACTIVE,
      memorySize: 512,
    });

    if (fn.role) {
      const secret = secretsmanager.Secret.fromSecretNameV2(
        this,
        "DiscogsSecret",
        "DiscogsPersonalAccessKey"
      );

      fn.role.addToPrincipalPolicy(
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ["secretsmanager:GetSecretValue"],
          resources: [secret.secretArn],
        })
      );

      secret.grantRead(fn.role);
    }

    this.hostedZone = HostedZone.fromLookup(this, "StaticWebsiteHostedZone", {
      domainName: "willkronberg.dev",
    });

    this.certificate = new DnsValidatedCertificate(this, "SSLCertificate", {
      domainName: "api.willkronberg.dev",
      hostedZone: this.hostedZone,
    });

    this.api = new RestApi(this, "WillKronbergRestApi", {
      restApiName: "WillKronbergRestApi",
      description: "runs all apis for frontend blog",
      cloudWatchRole: true,
      domainName: {
        domainName: "api.willkronberg.dev",
        certificate: this.certificate,
      },
      defaultCorsPreflightOptions: {
        allowCredentials: true,
        allowOrigins: Cors.ALL_ORIGINS,
        allowMethods: Cors.ALL_METHODS,
        allowHeaders: [
          "Content-Type",
          "X-Amz-Date",
          "Authorization",
          "X-Api-Key",
        ],
      },
    });

    const records = this.api.root.addResource("records");

    new ARecord(this, "SiteAliasRecord", {
      recordName: "api.willkronberg.dev",
      target: RecordTarget.fromAlias(new ApiGateway(this.api)),
      zone: this.hostedZone,
    });

    records.addMethod(
      "GET",
      new LambdaIntegration(fn, {
        allowTestInvoke: true,
      })
    );
  }
}
