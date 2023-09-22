# Attractor Subsystem
Attractor is a system of smart contracts that provides project users with the purchase and sale of the algorithmic stable coin **UBD**, as well as the management of liquidity received from users.  

## Main Contracts and Flow
- **Sandbox 1** - users buy UBD ERC20 tokens for USDT. USDT stored here until the Treasury is replenished;
**Once a day** Sandbox1 purchases WBTC and ETH at 50% equivalent to the value of 1% of the USDT volume stored in Sandbox 1 that day.
- **Treasury** - BTC/ETH 50%/50% is stored; Collateral is the amount of funds in the Sandbox1 plus the amount of funds in the Treasury, divided by the number of currently existing UBDs (UBD totalSypply).
- **Sandbox 2** - reserve for stabilizing supply in DAI. At the moment when UBD collateral is 3:1 or higher, then the Treasury exchanges 1/3 of its funds for DAI and transfers them to Sandbox2.  As soon as the collateral level approaches 0.5:1, Sandbox2 does the same as Sandbox 1: it replenishes the Treasury by 1% once a day through the purchase of WBTC and ETH. Sandbox2 turns off and stops replenishing the Treasury when the supply level reaches 1:1. Thus, Sandbox2 operates at a supply level of 0.5 to 1.
- **UBDToken** - United Blockchain Dollar (UBD) Stable Coin.
- **MarketRegistry** - encapsulate all assets managment logic and work with AMM(DEXes).
[Full Class Diagramm](./CLASSDIAGRAM.md)

## Deployments Insfo

### 2023-09-21 Attractor Contracts Set in Sepolia
[MarketRegistry](
https://sepolia.etherscan.io/address/0xCffDEa494e830Ef01d6cAbf0741b6B2a9733b683#code)  

[SandBox1](
https://sepolia.etherscan.io/address/0x9037e5D0a044F987Fd78b34080D826ba35aC1081#code)  

[SandBox2](
https://sepolia.etherscan.io/address/0x7cC5F6717Ff6C941B131E66ba1fb5B5b20fB894f#code)  

[Treasury](
https://sepolia.etherscan.io/address/0x86e1306Af4460f00a3D2B0Daee50eD7204210584#code)  

[UBDToken](
https://sepolia.etherscan.io/address/0xea458a3F46d27ae1ECF7CE67FD57954380e56E78#code)  


[MarketAdapterCustomMarket](
https://sepolia.etherscan.io/address/0x8aC7c971D0DA91034c75bA261ca67FF6c506F2fA#code)  


[MockSwapRouter](
https://sepolia.etherscan.io/address/0x73a3a59c1C36FA1DBBf799AA719c69a1B82f9A6C#code)  

 #### Test Assets
[USDT](
https://sepolia.etherscan.io/address/0xE3cfED0fbCDB7AaE09816718f0f52F10140Fc61F#code)  

[USDC](
https://sepolia.etherscan.io/address/0xBF8528699868B1a5279084C92B1d31D9C0160504#code)  

[DAI](
https://sepolia.etherscan.io/address/0xE52E3383740e713631864Af328717966F5Fa4e22#code)  

[WBTC](
https://sepolia.etherscan.io/address/0xa2535BFbe7c0b0EB7B494D70cf7f47e037e19b02#code)  