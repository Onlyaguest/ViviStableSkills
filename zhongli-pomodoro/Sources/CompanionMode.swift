import Foundation

enum CompanionMode: String {
    case pomodoro, codex
    func action(running: Bool, started: Bool, timerCelebrating: Bool, codex: String, codexCelebrating: Bool) -> String {
        switch self {
        case .pomodoro:
            if timerCelebrating { return "happy" }
            if running { return "read" }
            return started ? "piqued" : "doze"
        case .codex:
            if codex == "attention" || codex == "error" { return "piqued" }
            if codex == "working" { return "read" }
            return codexCelebrating ? "happy" : "doze"
        }
    }
}
func codexStatus(_ parsed: [String:Any], now: Date) -> String {
    guard let updated=parsed["lastUpdated"] as? Double,let value=parsed["status"] as? String else{return "unknown"}
    let age=now.timeIntervalSince1970-updated/1000
    guard age>=0 && age<600 else{return "unknown"}
    if value=="working" {
        if let attention=parsed["needsAttention"] as? String,!attention.isEmpty {return "attention"}
        if let attention=parsed["needsAttention"] as? Bool,attention {return "attention"}
    }
    return ["working","completed","idle","error"].contains(value) ? value : "unknown"
}
