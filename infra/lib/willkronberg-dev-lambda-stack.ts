import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as secretsmanager from "aws-cdk-lib/aws-secretsmanager";
import { Function, Runtime, Code, Tracing } from "aws-cdk-lib/aws-lambda";
import * as path from "path";
import { Effect, PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Duration } from "aws-cdk-lib";
import { Cors, LambdaIntegration, MethodLoggingLevel, RestApi } from "aws-cdk-lib/aws-apigateway";
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

    const getBlogArticlesHandler = new Function(
      this,
      "GetBlogArticlesHandler",
      {
        runtime: Runtime.PYTHON_3_9,
        handler: "willkronberg.handlers.get_articles_handler.get_articles_handler",
        code: Code.fromDockerBuild(path.join(__dirname, "..", "..")),
        timeout: Duration.seconds(30),
        tracing: Tracing.ACTIVE,
        memorySize: 512,
      }
    );

    const getCollectionHandler = new Function(this, "GetCollectionHandler", {
      runtime: Runtime.PYTHON_3_9,
      handler: "willkronberg.handlers.get_collection_handler.get_collection_handler",
      code: Code.fromDockerBuild(path.join(__dirname, "..", "..")),
      timeout: Duration.seconds(30),
      tracing: Tracing.ACTIVE,
      memorySize: 512,
    });

    if (getCollectionHandler.role) {
      const secret = secretsmanager.Secret.fromSecretNameV2(
        this,
        "DiscogsSecret",
        "DiscogsPersonalAccessKey"
      );

      getCollectionHandler.role.addToPrincipalPolicy(
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ["secretsmanager:GetSecretValue"],
          resources: [secret.secretArn],
        })
      );

      secret.grantRead(getCollectionHandler.role);
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
      deployOptions: {
        loggingLevel: MethodLoggingLevel.INFO,
        metricsEnabled: true,
        tracingEnabled: true,
        dataTraceEnabled: true,
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

    const articles = this.api.root.addResource("articles");

    articles.addMethod(
      "GET",
      new LambdaIntegration(getBlogArticlesHandler, {
        allowTestInvoke: true,
      })
    );

    const records = this.api.root.addResource("records");

    records.addMethod(
      "GET",
      new LambdaIntegration(getCollectionHandler, {
        allowTestInvoke: true,
      })
    );

    new ARecord(this, "SiteAliasRecord", {
      recordName: "api.willkronberg.dev",
      target: RecordTarget.fromAlias(new ApiGateway(this.api)),
      zone: this.hostedZone,
    });
  }
}
