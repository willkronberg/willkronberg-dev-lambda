#!/usr/bin/env node
import "source-map-support/register";
import { App } from "aws-cdk-lib";
import { WillkronbergDevLambdaStack } from "../lib/stacks/willkronberg-dev-lambda-stack";
import { WillkronbergDevMonitoringStack } from "../lib/stacks/willkronberg-dev-monitoring-stack";

const app = new App();

const lambdaStack = new WillkronbergDevLambdaStack(app, "WillkronbergDevLambdaStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

const monitoringStack = new WillkronbergDevMonitoringStack(app, "WillkronbergDevMonitoringStack", {
  api: lambdaStack.api,
  discogsSecret: lambdaStack.discogsSecret,
  lambdaFunctions: [lambdaStack.getBlogArticlesHandler, lambdaStack.getCollectionHandler]
})

monitoringStack.addDependency(lambdaStack);