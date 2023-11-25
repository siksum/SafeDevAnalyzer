<script src='https://unpkg.com/mermaid@8.1.0/dist/mermaid.min.js'></script>

<link rel="stylesheet" href="css/jquery.markdown.css" type="text/css" />
<div id="markdown-editor"></div>
<script type="text/javascript" src="css/jquery.markdown.js"></script>

## multi select

<select class="test">
  <option value="1">American Black Bear</option>
  <option value="2">Asiatic Black Bear</option>
  <option value="3">Brown Bear</option>
  <option value="4">Giant Panda</option>
  <option value="5">Sloth Bear</option>
  <option value="6">Sun Bear</option>
  <option value="7">Polar Bear</option>
  <option value="8">Spectacled Bear</option>
</select>

<script type="text/javascript">
    $(document).ready(function () {
    $("#test").CreateMultiCheckBox({ width: '230px',
                defaultText : 'Select Below', height:'250px' });
    });
</script>

<style>
.test{
    background-color:pink;
}
</style>

<div class='mermaid'>
classDiagram
	class GuessTheRandomNumber{
		guess
		constructor
	}
	class Solidity{
		blockhash(uint256)
		abi.encodePacked()
		keccak256(bytes)
		require(bool,string)
	}
GuessTheRandomNumber --|> Solidity
</div>
