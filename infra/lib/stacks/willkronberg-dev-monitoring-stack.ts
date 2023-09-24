import { Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import { MonitoringFacade } from "cdk-monitoring-constructs"
import { WoolyLambdaFunction } from "../constructs/lambda-function";
import { IRestApi } from "aws-cdk-lib/aws-apigateway";
import { ISecret } from "aws-cdk-lib/aws-secretsmanager";

export interface Props extends StackProps {
    api: IRestApi;
    lambdaFunctions: WoolyLambdaFunction[];
    discogsSecret: ISecret;
}

export class WillkronbergDevMonitoringStack extends Stack {
    private readonly monitoring: MonitoringFacade

    constructor(scope: Construct, id: string, props: Props) {
        super(scope, id, props)

        this.monitoring = new MonitoringFacade(this, "WillkronbergDevMonitoringFacade")

        this.monitoring.monitorApiGateway({ api: props.api })

        for (const woolyFunction of props.lambdaFunctions) {
            this.monitoring.monitorLambdaFunction({
                lambdaFunction: woolyFunction.lambdaFunction
            })
        }

        this.monitoring.monitorSecretsManagerSecret({ secret: props.discogsSecret, humanReadableName: "Discogs Access Token" })
    }
}