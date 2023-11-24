<pre class="mermaid">
classDiagram
    class GuessTheRandomNumber{
        guess()
        constructor()
    }
    class Solidity{
        blockhash(uint256)
        abi.encodePacked()
        keccak256(bytes)
        require(bool,string)
    }
    GuessTheRandomNumber --|> Solidity
</pre>