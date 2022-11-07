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
import { CfnWebACL, CfnWebACLAssociation } from "aws-cdk-lib/aws-wafv2";

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
        handler: "willkronberg.app.get_articles_handler",
        code: Code.fromDockerBuild(path.join(__dirname, "..", "..")),
        timeout: Duration.seconds(30),
        tracing: Tracing.ACTIVE,
        memorySize: 512,
      }
    );

    if (getBlogArticlesHandler.role) {
      const secret = secretsmanager.Secret.fromSecretNameV2(
        this,
        "RapidApiSecret",
        "Rapid-API-Key"
      );

      getBlogArticlesHandler.role.addToPrincipalPolicy(
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ["secretsmanager:GetSecretValue"],
          resources: [secret.secretArn],
        })
      );

      secret.grantRead(getBlogArticlesHandler.role);
    }

    const getCollectionHandler = new Function(this, "GetCollectionHandler", {
      runtime: Runtime.PYTHON_3_9,
      handler: "willkronberg.app.get_collection_handler",
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

    const webACL = new CfnWebACL(this, "ApiWebACL", {
      name: "ApiWebACL",
      defaultAction: {
        allow: {},
      },
      scope: "REGIONAL",
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "MetricForApiACL",
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: "CRSRule",
          priority: 0,
          statement: {
            managedRuleGroupStatement: {
              name: "AWSManagedRulesCommonRuleSet",
              vendorName: "AWS",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "API-ACL-CRS",
            sampledRequestsEnabled: true,
          },
          overrideAction: {
            none: {},
          },
        },
        {
          name: "ThrottlingBlanketRule",
          priority: 1,
          statement: {
            rateBasedStatement: {
              limit: 7000,
              aggregateKeyType: "IP",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "API-ACL-ThrottlingBlanket",
            sampledRequestsEnabled: true,
          },
          action: {
            block: {},
          },
        },
      ],
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

    new CfnWebACLAssociation(this, "ApiWebACLAssociation", {
      resourceArn: this.api.deploymentStage.stageArn,
      webAclArn: webACL.attrArn,
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
