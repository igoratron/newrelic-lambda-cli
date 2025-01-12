import click


def check_permissions(session, actions, resources=None, context=None):
    """
    Checks whether an IAM user can perform specified actions. Also optionally checks
    actions against AWS resources and/or contexts.

    :param session: A boto3 session instance
    :param actions: A list of AWS actions to check
    :param resources: An optional list of AWS resources to check actions against
    :param context: Optional AWS contexts to check actions against
    :returns: A list of actions denied by AWS due to insufficient permissions
    :rtype: list
    """
    if not actions:
        return []

    actions = list(set(actions))

    if resources is None:
        resources = ["*"]

    context_entries = [{}]
    if context is not None:
        context_entries = [
            {
                "ContextKeyName": key,
                "ContextKeyValues": [str(val) for val in values],
                "ContextKeyType": "string",
            }
            for key, values in context.items()
        ]

    # docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html
    iam = session.client("iam")
    sts = session.client("sts")

    # docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts.html#STS.Client.get_caller_identity
    caller = sts.get_caller_identity()
    caller_arn = caller["Arn"]

    # docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.simulate_principal_policy
    results = iam.simulate_principal_policy(
        PolicySourceArn=caller_arn,
        ActionNames=actions,
        ResourceArns=resources,
        ContextEntries=context_entries,
    )["EvaluationResults"]

    return sorted(
        [
            result["EvalActionName"]
            for result in results
            if result["EvalDecision"] != "allowed"
        ]
    )


def ensure_integration_install_permissions(session):
    """
    Ensures that the current AWS session has the necessary permissions to install the
    New Relic AWS Lambda Integration.

    :param session: A boto3 session
    """
    needed_permissions = check_permissions(
        session,
        actions=[
            "cloudformation:CreateChangeSet",
            "cloudformation:CreateStack",
            "cloudformation:DescribeStacks",
            "iam:AttachRolePolicy",
            "iam:CreateRole",
            "iam:GetRole",
            "iam:PassRole",
            "lambda:AddPermission",
            "lambda:CreateFunction",
            "lambda:GetFunction",
            "logs:DeleteSubscriptionFilter",
            "logs:DescribeSubscriptionFilters",
            "logs:PutSubscriptionFilter",
            "s3:GetObject",
        ],
    )

    if needed_permissions:
        message = [
            "The following AWS permissions are needed to install the New RElic AWS "
            "Lambda integration:\n"
        ]
        for needed_permission in needed_permissions:
            message.append(" * %s" % needed_permission)
        message.append("\nEnsure your AWS user has these permissions and try again.")
        raise click.UsageError("\n".join(message))


def ensure_integration_uninstall_permissions(session):
    """
    Ensures that the current AWS session has the necessary permissions to uninstall the
    New Relic AWS Lambda Integration.

    :param session: A boto3 session
    """
    needed_permissions = check_permissions(
        session,
        actions=[
            "cloudformation:DeleteStack",
            "cloudformation:DescribeStacks",
            "lambda:GetFunction",
            "logs:DeleteSubscriptionFilter",
        ],
    )

    if needed_permissions:
        message = [
            "The following AWS permissions are needed to uninstall the New RElic AWS "
            "Lambda integration:\n"
        ]
        for needed_permission in needed_permissions:
            message.append(" * %s" % needed_permission)
        message.append("\nEnsure your AWS user has these permissions and try again.")
        raise click.UsageError("\n".join(message))


def ensure_lambda_install_permissions(session):
    """
    Ensures that the current AWS session has the necessary permissions to install the
    New Relic AWS Lambda layer and log subscription.

    :param session: A boto3 session
    """
    needed_permissions = check_permissions(
        session,
        actions=[
            "lambda:GetFunction",
            "lambda:UpdateFunctionConfiguration",
            "logs:DeleteSubscriptionFilter",
            "logs:DescribeSubscriptionFilters",
            "logs:PutSubscriptionFilter",
        ],
    )

    if needed_permissions:
        message = [
            "The following AWS permissions are needed to install the New RElic AWS Lambda layer:\n"
        ]

        for needed_permission in needed_permissions:
            message.append(" * %s" % needed_permission)

        message.append("\nEnsure your AWS user has these permissions and try again.")

        raise click.UsageError("\n".join(message))


def ensure_lambda_uninstall_permissions(session):
    """
    Ensures that the current AWS session has the necessary permissions to uninstall the
    New Relic AWS Lambda layer and log subscription.

    :param session: A boto3 session
    """
    needed_permissions = check_permissions(
        session,
        actions=[
            "lambda:GetFunction",
            "lambda:UpdateFunctionConfiguration",
            "logs:DeleteSubscriptionFilter",
            "logs:DescribeSubscriptionFilters",
        ],
    )

    if needed_permissions:
        message = [
            "The following AWS permissions are needed to uninstall the New RElic AWS "
            "Lambda layer:\n"
        ]
        for needed_permission in needed_permissions:
            message.append(" * %s" % needed_permission)
        message.append("\nEnsure your AWS user has these permissions and try again.")
        raise click.UsageError("\n".join(message))


def ensure_lambda_list_permissions(session):
    """
    Ensures that the current AWS session has the necessary permissions to list the functions
    with New Relic AWS Lambda layers.

    :param session: A boto3 session
    """
    needed_permissions = check_permissions(session, actions=["lambda:ListFunctions"])

    if needed_permissions:
        message = ["The following AWS permissions are needed to list functions:\n"]
        for needed_permission in needed_permissions:
            message.append(" * %s" % needed_permission)
        message.append("\nEnsure your AWS user has these permissions and try again.")
        raise click.UsageError("\n".join(message))
