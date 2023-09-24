import { Duration } from "aws-cdk-lib";
import { Effect, PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Code, Function, Runtime, Tracing } from "aws-cdk-lib/aws-lambda";
import { ISecret } from "aws-cdk-lib/aws-secretsmanager";
import { Construct } from "constructs";
import * as path from "path";

export interface Props {
    name: string;
    handler: string;
    memorySize?: number;
    timeout?: Duration;
    secrets?: ISecret[];
}

export class WoolyLambdaFunction extends Construct {
    public lambdaFunction: Function

    constructor(scope: Construct, id: string, props: Props) {
        super(scope, id);

        this.lambdaFunction = new Function(this, props.name, {
            functionName: props.name,
            runtime: Runtime.PYTHON_3_11,
            handler: props.handler,
            code: Code.fromDockerBuild(path.join(__dirname, "..", "..", "..")),
            timeout: props.timeout || Duration.seconds(30),
            tracing: Tracing.ACTIVE,
            memorySize: props.memorySize,
            environment: {
                POWERTOOLS_SERVICE_NAME: "api.willkronberg.dev",
                LOG_LEVEL: "INFO",
            },
        });

        if (props.secrets) {
            if (!this.lambdaFunction.role) {
                throw new Error("Missing IAM Role for Lambda Function")
            }

            for (const secret of props.secrets) {
                this.lambdaFunction.role.addToPrincipalPolicy(
                    new PolicyStatement({
                        effect: Effect.ALLOW,
                        actions: ["secretsmanager:GetSecretValue"],
                        resources: [secret.secretArn],
                    })
                );

                secret.grantRead(this.lambdaFunction.role);
            }
        }
    }
}