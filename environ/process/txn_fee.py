"""
Functions to calculate transaction fee and adjust the return
"""

import pandas as pd

from environ.constants import INITIAL_WEALTH, TRANSACTION_COST


def wealth(
    ret_df: pd.DataFrame,
    wgt_df: pd.DataFrame,
    initial_wealth: float = INITIAL_WEALTH,
    transaction_cost_rate: float = TRANSACTION_COST,
) -> dict[str, list[str | float]]:
    """
    Function to calculate the wealth dynamics
    """

    date_list = sorted(wgt_df["quarter"].unique().tolist())

    wgt_df_without_cash = wgt_df[wgt_df["name"] != "Cash"].copy()
    wgt_df_without_cash.sort_values(["quarter", "name"], inplace=True)

    wealth_dict = {
        "date": [],
        "wealth": [],
    }

    for idx, date in enumerate(date_list):
        wealth_dict["date"].append(date)

        wgt_vec_without_cash = wgt_df_without_cash.loc[
            wgt_df_without_cash["quarter"] == date, "weight"
        ]

        if idx == 0:
            # open position
            wealth_dict["wealth"].append(
                initial_wealth
                - initial_wealth
                * wgt_vec_without_cash.sum()  # type: ignore
                * transaction_cost_rate
            )
        else:
            investment_value_before_ret = wealth_dict["wealth"][-1]

            if idx == len(date_list) - 1:
                # close position
                cum_ret = (
                    ret_df.loc[
                        (ret_df.index >= date),
                        "ret",
                    ]
                    + 1
                ).prod() - 1  # type: ignore
                investment_value_after_ret_before_fee = investment_value_before_ret * (
                    cum_ret + 1
                )
                wealth_dict["wealth"].append(
                    investment_value_after_ret_before_fee
                    - investment_value_after_ret_before_fee
                    * wgt_vec_without_cash.sum()  # type: ignore
                    * transaction_cost_rate
                )

            else:
                # rebalance
                cum_ret = (
                    ret_df.loc[
                        (ret_df.index >= date) & (ret_df.index < date_list[idx + 1]),
                        "ret",
                    ]
                    + 1
                ).prod() - 1  # type: ignore
                investment_value_after_ret_before_fee = investment_value_before_ret * (
                    cum_ret + 1
                )
                wgt_vec_without_cash_next = wgt_df_without_cash.loc[
                    wgt_df_without_cash["quarter"] == date_list[idx + 1], "weight"
                ]
                investment_value_after_fee = (
                    investment_value_after_ret_before_fee
                    - investment_value_after_ret_before_fee
                    * (
                        abs(
                            wgt_vec_without_cash_next.values  # type: ignore
                            - wgt_vec_without_cash.values  # type: ignore
                        ).sum()
                        * transaction_cost_rate
                    )
                )
                wealth_dict["wealth"].append(investment_value_after_fee)

    return wealth_dict


if __name__ == "__main__":
    ret_test = pd.DataFrame(
        {"ret": [1, 1, 1]},
        index=["2000-01-01", "2000-04-01", "2000-07-01"],
    ).rename_axis("date")

    wgt_test = pd.DataFrame(
        {
            "quarter": [
                "2000-01-01",
                "2000-04-01",
                "2000-07-01",
                "2000-01-01",
                "2000-04-01",
                "2000-07-01",
            ],
            "name": ["Cash", "Cash", "Cash", "BTC", "BTC", "BTC"],
            "weight": [0.5, 0.6, 0.7, 0.5, 0.4, 0.3],
        }
    )

    print(wealth(ret_test, wgt_test))