import Foundation
@main struct ModeTests {
 static func main(){
  assert(CompanionMode.codex.action(running:true,started:true,timerCelebrating:false,codex:"attention",codexCelebrating:false)=="piqued")
  assert(CompanionMode.codex.action(running:true,started:true,timerCelebrating:false,codex:"completed",codexCelebrating:true)=="happy")
  assert(CompanionMode.pomodoro.action(running:true,started:true,timerCelebrating:false,codex:"attention",codexCelebrating:true)=="read")
  assert(CompanionMode.pomodoro.action(running:false,started:false,timerCelebrating:true,codex:"working",codexCelebrating:false)=="happy")
  let now=Date(timeIntervalSince1970:1000)
  assert(codexStatus(["status":"working","lastUpdated":1000000.0,"needsAttention":false],now:now)=="working")
  assert(codexStatus(["status":"working","lastUpdated":1000000.0,"needsAttention":"AskUserQuestion"],now:now)=="attention")
  assert(codexStatus(["status":"working","lastUpdated":1000000.0,"needsAttention":NSNull()],now:now)=="working")
  assert(codexStatus(["status":"working","lastUpdated":400000.0],now:now)=="unknown")
  assert(codexStatus(["status":"completed","lastUpdated":1001000.0],now:now)=="unknown")
  print("PASS: independent mode priorities and Codex attention/stale-source parsing")
 }
}
