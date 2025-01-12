from . import utils


def list_functions(session, filter_choice):
    client = session.client("lambda")

    # set all if the filter_choice is "all" or there is no filter_choice active.
    all = filter_choice == "all" or not filter_choice

    pager = client.get_paginator("list_functions")
    for func_resp in pager.paginate():
        funcs = func_resp.get("Functions", [])

        for f in funcs:
            f.setdefault("x-new-relic-enabled", False)
            for layer in f.get("Layers", []):
                if layer.get("Arn", "").startswith(
                    utils.get_arn_prefix(session.region_name)
                ):
                    f["x-new-relic-enabled"] = True
            if all:
                yield f
            elif filter_choice == "installed" and f["x-new-relic-enabled"]:
                yield f
            elif filter_choice == "not_installed" and not f["x-new-relic-enabled"]:
                yield f
