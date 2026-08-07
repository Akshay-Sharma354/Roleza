from app.services.greenhouse import fetch_greenhouse_board


COMPANY_WATCHLIST = {
    "Anthropic": {
        "ats": "greenhouse",
        "board_token": "anthropic",
    },
    "Together AI": {
        "ats": "greenhouse",
        "board_token": "togetherai",
    },
}


def fetch_company_watchlist_jobs():
    jobs = []
    errors = []

    for company_name, config in COMPANY_WATCHLIST.items():
        ats = config.get("ats")
        board_token = config.get("board_token")

        if ats != "greenhouse":
            continue

        try:
            company_jobs = fetch_greenhouse_board(
                company_name,
                board_token,
            )

            jobs.extend(company_jobs)

        except Exception as error:
            errors.append(
                f"{company_name}: {error}"
            )

    return {
        "jobs": jobs,
        "errors": errors,
        "companies": list(
            COMPANY_WATCHLIST.keys()
        ),
    }
