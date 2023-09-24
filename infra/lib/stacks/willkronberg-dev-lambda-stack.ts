import { Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import { ISecret, Secret } from "aws-cdk-lib/aws-secretsmanager";
import { Cors, LambdaIntegration, MethodLoggingLevel, RestApi } from "aws-cdk-lib/aws-apigateway";
import { Certificate, ValidationMethod } from "aws-cdk-lib/aws-certificatemanager";
import {
  ARecord,
  HostedZone,
  IHostedZone,
  RecordTarget,
} from "aws-cdk-lib/aws-route53";
import { ApiGateway } from "aws-cdk-lib/aws-route53-targets";
import { WoolyLambdaFunction } from "../constructs/lambda-function";

export class WillkronbergDevLambdaStack extends Stack {
  public readonly api: RestApi;
  public readonly getBlogArticlesHandler: WoolyLambdaFunction;
  public readonly getCollectionHandler: WoolyLambdaFunction;
  public readonly discogsSecret: ISecret;
  private readonly certificate: Certificate;
  private readonly hostedZone: IHostedZone;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    this.getBlogArticlesHandler = new WoolyLambdaFunction(this, "GetBlogArticlesHandler", {
      name: "GetBlogArticlesHandler",
      handler: "willkronberg.handlers.get_articles_handler.get_articles_handler",
    })

    this.discogsSecret = Secret.fromSecretNameV2(
      this,
      "DiscogsSecret",
      "DiscogsPersonalAccessKey"
    )

    this.getCollectionHandler = new WoolyLambdaFunction(this, "GetCollectionHandler", {
      name: "GetCollectionHandler",
      handler: "willkronberg.handlers.get_collection_handler.get_collection_handler",
      secrets: [this.discogsSecret]
    })

    this.hostedZone = HostedZone.fromLookup(this, "RootHostedZone", {
      domainName: "willkronberg.dev",
    });

    this.certificate = new Certificate(this, "SSLCertificate", {
      domainName: "api.willkronberg.dev",
      validation: {
        method: ValidationMethod.DNS,
        props: {
          hostedZone: this.hostedZone,
        }
      }
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
      new LambdaIntegration(this.getBlogArticlesHandler.lambdaFunction, {
        allowTestInvoke: true,
      })
    );

    const records = this.api.root.addResource("records");

    records.addMethod(
      "GET",
      new LambdaIntegration(this.getCollectionHandler.lambdaFunction, {
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
