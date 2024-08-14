```mermaid
classDiagram
	class EtherStore{
		guess
		deposit
		reward
		getBalance
		withdraw
	}
	class Solidity{
		require(bool,string)
		keccak256(bytes)
		abi.encodePacked()
		blockhash(uint256)
		require(bool,string)
		balance(address)
	}
EtherStore --|> Solidity
EtherStore --|> EtherStore
```