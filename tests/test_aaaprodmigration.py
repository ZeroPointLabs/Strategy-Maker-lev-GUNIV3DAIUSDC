import pytest
from brownie import chain, reverts, Contract, ZERO_ADDRESS


def test_prod_migration_scale_down(
    chain,
    token,
    amount,
    Strategy,
    gov,
    RELATIVE_APPROX,
    usdc,
    accounts,
    maxIL,
    setNewHealthCheck
):
    strategy = Contract("0xD1a12D62e434F9A4b8b1ebEBff644eeF8Cb79148")
    if (strategy.isActive() == False):
        assert 0 == 1
    sms = accounts.at(strategy.strategist(), force=True)
    vault = Contract(strategy.vault()) 
    strategy_assets_before = strategy.estimatedTotalAssets()
    strategy_debt_before = vault.strategies(strategy)["totalDebt"]

    # migrate to a new strategy
    new_strategy = sms.deploy(Strategy, vault, "Strategy-Maker-lev-GUNIDAIUSDC-0.01%")
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    orig_cdp_id = strategy.cdpId()
    new_strategy.shiftToCdp(orig_cdp_id, {"from": gov})
    assert new_strategy.estimatedTotalAssets() == strategy_assets_before 
    assert vault.strategies(new_strategy)["totalDebt"] == strategy_debt_before

    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL #there can be small amounts of realized IL

    ## scale strategy down
    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    chain.mine(1)
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

def test_prod_migration_scale_up_then_down(
    chain,
    token,
    amount,
    Strategy,
    gov,
    RELATIVE_APPROX,
    usdc,
    accounts,
    maxIL,
    setNewHealthCheck
):
    strategy = Contract("0xD1a12D62e434F9A4b8b1ebEBff644eeF8Cb79148")
    if (strategy.isActive() == False):
        assert 0 == 1
    sms = accounts.at(strategy.strategist(), force=True)
    vault = Contract(strategy.vault()) 
    strategy_assets_before = strategy.estimatedTotalAssets()
    strategy_debt_before = vault.strategies(strategy)["totalDebt"]

    # migrate to a new strategy
    new_strategy = sms.deploy(Strategy, vault, "Strategy-Maker-lev-GUNIDAIUSDC-0.01%")
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    orig_cdp_id = strategy.cdpId()
    new_strategy.shiftToCdp(orig_cdp_id, {"from": gov})
    assert new_strategy.estimatedTotalAssets() == strategy_assets_before 
    assert vault.strategies(new_strategy)["totalDebt"] == strategy_debt_before

    ##scale up using genlev funds from vault:
    genlev = Contract("0x1676055fE954EE6fc388F9096210E5EbE0A9070c")
    genlev.setEmergencyExit({"from": gov})
    genlev.setDoHealthCheck(False, {"from": gov})
    genlev.harvest({"from": gov})

    ##give dr to new_strategy:
    vault.updateStrategyDebtRatio(new_strategy, vault.strategies(new_strategy)["debtRatio"]+10000-vault.debtRatio(), {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    ##play around with dr:
    vault.updateStrategyDebtRatio(new_strategy, 1000, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 1000+10000-vault.debtRatio(), {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 1000, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 300, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

def test_prod_migration_harvest_scale_up_then_down(
    chain,
    token,
    amount,
    Strategy,
    gov,
    RELATIVE_APPROX,
    usdc,
    accounts,
    maxIL,
    setNewHealthCheck
):
    strategy = Contract("0xD1a12D62e434F9A4b8b1ebEBff644eeF8Cb79148")
    if (strategy.isActive() == False):
        assert 0 == 1
    sms = accounts.at(strategy.strategist(), force=True)
    vault = Contract(strategy.vault()) 
    strategy_assets_before = strategy.estimatedTotalAssets()
    strategy_debt_before = vault.strategies(strategy)["totalDebt"]

    # migrate to a new strategy
    new_strategy = sms.deploy(Strategy, vault, "Strategy-Maker-lev-GUNIDAIUSDC-0.01%")
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    orig_cdp_id = strategy.cdpId()
    new_strategy.shiftToCdp(orig_cdp_id, {"from": gov})
    assert new_strategy.estimatedTotalAssets() == strategy_assets_before 
    assert vault.strategies(new_strategy)["totalDebt"] == strategy_debt_before

    ##scale up using genlev funds from vault:
    genlev = Contract("0x1676055fE954EE6fc388F9096210E5EbE0A9070c")
    genlev.setEmergencyExit({"from": gov})
    genlev.setDoHealthCheck(False, {"from": gov})
    genlev.harvest({"from": gov})

    ##give dr to new_strategy:
    vault.updateStrategyDebtRatio(new_strategy, vault.strategies(new_strategy)["debtRatio"]+10000-vault.debtRatio(), {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    ##play around with dr:
    vault.updateStrategyDebtRatio(new_strategy, 1000, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 1000+10000-vault.debtRatio(), {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    new_strategy.setDoHealthCheck(False, {"from": gov})

    vault.updateStrategyDebtRatio(new_strategy, 1000, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 300, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL



def test_prod_migration_harvest_scale_up_then_profits_then_down(
    chain,
    token,
    amount,
    Strategy,
    gov,
    RELATIVE_APPROX,
    usdc,
    accounts,
    token_whale,
    partnerToken,
    maxIL,
    setNewHealthCheck
):
    strategy = Contract("0xD1a12D62e434F9A4b8b1ebEBff644eeF8Cb79148")
    if (strategy.isActive() == False):
        assert 0 == 1
    sms = accounts.at(strategy.strategist(), force=True)
    vault = Contract(strategy.vault()) 
    strategy_assets_before = strategy.estimatedTotalAssets()
    strategy_debt_before = vault.strategies(strategy)["totalDebt"]

    # migrate to a new strategy
    new_strategy = sms.deploy(Strategy, vault, "Strategy-Maker-lev-GUNIDAIUSDC-0.01%")
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    orig_cdp_id = strategy.cdpId()
    new_strategy.shiftToCdp(orig_cdp_id, {"from": gov})
    assert new_strategy.estimatedTotalAssets() == strategy_assets_before 
    assert vault.strategies(new_strategy)["totalDebt"] == strategy_debt_before

    ##scale up using genlev funds from vault:
    genlev = Contract("0x1676055fE954EE6fc388F9096210E5EbE0A9070c")
    genlev.setEmergencyExit({"from": gov})
    genlev.setDoHealthCheck(False, {"from": gov})
    genlev.harvest({"from": gov})

    ##give dr to new_strategy:
    vault.updateStrategyDebtRatio(new_strategy, vault.strategies(new_strategy)["debtRatio"]+10000-vault.debtRatio(), {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    #Create profits for UNIV3 DAI<->USDC
    uniswapv3 = Contract("0xE592427A0AEce92De3Edee1F18E0157C05861564")
    #token --> partnerToken
    uniswapAmount = token.balanceOf(token_whale)*0.1
    token.approve(uniswapv3, uniswapAmount, {"from": token_whale})
    uniswapv3.exactInputSingle((token, partnerToken, 100, token_whale, 1856589943, uniswapAmount, 0, 0), {"from": token_whale})
    chain.sleep(1)

    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    ##play around with dr:
    vault.updateStrategyDebtRatio(new_strategy, 1000, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 1000+10000-vault.debtRatio(), {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    new_strategy.setDoHealthCheck(False, {"from": gov})
     

    vault.updateStrategyDebtRatio(new_strategy, 1000, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 300, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    vault.updateStrategyDebtRatio(new_strategy, 0, {"from": gov})
    new_strategy.setDoHealthCheck(False, {"from": gov})
    new_strategy.harvest({"from": gov})
    assert vault.strategies(new_strategy)["totalLoss"] < maxIL

    if new_strategy.estimatedTotalAssets() > 0:
        ## scale strategy down
        new_strategy.setDoHealthCheck(False, {"from": gov})
        new_strategy.harvest({"from": gov})
        assert vault.strategies(new_strategy)["totalLoss"] < maxIL






