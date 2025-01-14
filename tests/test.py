import pytest
import brownie
from brownie import config, Contract, accounts, interface, chain
from brownie import network


def test_operation(donator, sms, ychad, yvboost, rando, chain):
    tx = yvboost.transfer(donator, yvboost.balanceOf(sms), {"from":sms})
    assert yvboost.balanceOf(donator) > 0
    yvboost = interface.IVault(yvboost)
    starting_total_supply = yvboost.totalSupply()
    yveCrv = Contract(yvboost.token())
    starting_bal_donator = yvboost.balanceOf(donator)
    starting_bal_yveCrv = yveCrv.balanceOf(yvboost)

    tx = donator.donate({"from":rando})
    print(tx.events["Donated"])
    with brownie.reverts():
        donator.donate({"from":rando}) # Should fail due to too soon
    chain.sleep(60 * 60 * 24 * 2)
    chain.snapshot()
    donator.donate({"from":rando})
    chain.revert()
    assert tx.events["Donated"]["amountBurned"] == starting_total_supply - yvboost.totalSupply()
    assert tx.events["Donated"]["amountBurned"] == starting_bal_donator - yvboost.balanceOf(donator)
    assert yveCrv.balanceOf(yvboost) >= starting_bal_yveCrv

def test_change_gov(donator, sms, ychad, yvboost, rando, chain):
    with brownie.reverts():
        donator.setGovernance(rando, {"from":rando})
    donator.setGovernance(ychad, {"from":sms})
    assert donator.governance() == sms
    donator.acceptGovernance({"from":ychad})

def test_sweep(donator, sms, ychad, yvboost, dai, rando, chain):
    before_balance = dai.balanceOf(sms)
    with brownie.reverts():
        donator.sweep(yvboost, {"from":rando})
    donator.sweep(yvboost, {"from":sms})
    donator.sweep(dai, {"from":sms})
    assert dai.balanceOf(sms) > before_balance

def test_set_donate_interval(donator, sms, ychad, yvboost, rando, chain):
    with brownie.reverts():
        donator.setDonateInterval(100, {"from":rando})
    donator.setDonateInterval(100, {"from":sms})
    assert donator.donateInterval() == 100

def test_set_max_burn_amount(donator, sms, ychad, yvboost, rando, chain):
    with brownie.reverts():
        donator.setMaxBurnAmount(1_000, {"from":rando})
    donator.setMaxBurnAmount(100, {"from":sms})
    assert donator.maxBurnAmount() == 100