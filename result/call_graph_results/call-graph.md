```mermaid
classDiagram
	class Attack{
		constructor
		attack
	}
	class Solidity{
		require(bool,string)
		balance(address)
	}
Attack --|> Solidity

```