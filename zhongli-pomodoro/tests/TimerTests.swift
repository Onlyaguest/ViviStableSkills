import Foundation
@main struct TimerTests {
 static func main() {
  let t = Date(timeIntervalSince1970: 1000)
  var p = Pomodoro()
  assert(!p.toggle(at:t))
  assert(p.seconds(at:t.addingTimeInterval(60)) == 1440)
  p.toggle(at:t.addingTimeInterval(60)); assert(!p.running && p.remaining == 1440)
  p.toggle(at:t.addingTimeInterval(600)); assert(p.seconds(at:t.addingTimeInterval(601)) == 1439)
  assert(p.tick(at:t.addingTimeInterval(2040))); assert(p.completed == 1 && p.phase == .shortBreak)
  assert(!p.tick(at:t.addingTimeInterval(3000)))
  assert(p.toggle(at:t.addingTimeInterval(3000)))
  p.toggle(at:t.addingTimeInterval(3010)); assert(!p.toggle(at:t.addingTimeInterval(3020)))
  assert(p.tick(at:t.addingTimeInterval(4000))); assert(p.phase == .focus && p.completed == 1)
  p.completed=3; p.toggle(at:t); assert(p.tick(at:t.addingTimeInterval(1500))); assert(p.phase == .longBreak)
  assert(!p.toggle(at:t.addingTimeInterval(1600)))
  let restored=p.snapshot(at:t.addingTimeInterval(1660)); assert(!restored.running && restored.remaining==840 && restored.valid)
  p.reset(); assert(p.remaining==1500 && p.completed==4 && !p.started)
  print("PASS: pause/resume, exact completion, no duplicate completion, short-break voice, long break, paused restoration")
 }
}
