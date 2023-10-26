vulnerabilities = {
    "lending/EtherStore.sol": {
        "type": "reentrancy",
        "severity": "high"
    },
    "lending/Front.sol": {
        "type": "front-running",
        "severity": "low"
    },
    "lending/Akropolis.sol": {
        "type": "re-entrancy",
        "severity": "high",
        "etherscan": "https://etherscan.io/address/0x73fC3038B4cD8FfD07482b92a52Ea806505e5748#code",
        "description": "## Reentrancy \n\n ### Definition : \n- Reentrancy is a vulnerability that allows a function to repeatedly call another function within a contract before completing the previous execution.\n- This typically occurs when an internal contract calls an external contract. \n\n ### example : \n- When contract A calls contract B, B's code is executed.\n- If contract B then calls a function within contract A, it permits reentry, potentially leading to changes in A's state.\n- Reentrancy is particularly risky in financial operations.\n- If contract A sends ether to contract B and B subsequently calls a function in A to return the ether, A may process the funds within B's function, creating an opportunity for an attacker to repeatedly siphon off ether.\n\n### Prevention :\n- To prevent Reentrancy vulnerabilities, it's essential to modify the state before making external calls or employ locking mechanisms when necessary to thwart attacks and enhance security."
    }

}

def get_vulnerability_info(path):
    if path in vulnerabilities:
        vulnerability_info = vulnerabilities[path]
        vuln_type = vulnerability_info["type"]
        severity = vulnerability_info["severity"]
        etherscan = vulnerability_info["etherscan"]
        description = vulnerability_info["description"]
        return vuln_type, severity, etherscan, description
    else:
        print("Vulnerability information not found")

def vuln(path):
    vuln_type, severity, etherscan, description = get_vulnerability_info(path)
    if vuln_type is not None and severity is not None:
        return vuln_type, severity, etherscan, description
    else:
        print("Vulnerability information not found")