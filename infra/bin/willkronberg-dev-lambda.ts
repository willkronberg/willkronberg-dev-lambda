#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { WillkronbergDevLambdaStack } from "../lib/willkronberg-dev-lambda-stack";

const app = new cdk.App();
new WillkronbergDevLambdaStack(app, "WillkronbergDevLambdaStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
