# contract address 클릭하면 해당 컨트랙트의 etherscan 주소로 넘어가도록, (description 간단하게 + to-be 코드) 
vulnerabilities = {
    "lending/EtherStore.sol": {
        "type": "reentrancy",
        "severity": "high"
    },
    "lending/Front.sol": {
        "type": "front-running",
        "severity": "low"
    }
}

def get_vulnerability_info(path):
    if path in vulnerabilities:
        vulnerability_info = vulnerabilities[path]
        vuln_type = vulnerability_info["type"]
        severity = vulnerability_info["severity"]
        return vuln_type, severity

def vuln(path):
    vuln_type, severity = get_vulnerability_info(path)
    if vuln_type is not None and severity is not None:
        return vuln_type, severity
    else:
        print("Vulnerability information not found")
