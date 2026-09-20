def count_parameters(model):

    total = sum(
        parameter.numel()
        for parameter in model.parameters()
    )
    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return total, trainable


def parameter_breakdown(model):

    seen_parameters = set()
    breakdown = {}

    for name, module in model.named_children():

        component_total = 0

        for parameter in module.parameters():

            parameter_id = id(parameter)

            if parameter_id not in seen_parameters:
                component_total += parameter.numel()
                seen_parameters.add(parameter_id)

        breakdown[name] = component_total

    return breakdown
