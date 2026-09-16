import Foundation

struct Pomodoro: Codable {
    enum Phase: String, Codable { case focus, shortBreak, longBreak
        var duration: TimeInterval { self == .focus ? 1500 : self == .shortBreak ? 300 : 900 }
        var name: String { self == .focus ? "专注" : "休息" }
    }
    var phase: Phase = .focus
    var remaining: TimeInterval = 1500
    var running = false
    var deadline: Date?
    var completed = 0
    var started = false

    func seconds(at now: Date) -> TimeInterval {
        running ? max(0, (deadline ?? now).timeIntervalSince(now)) : remaining
    }
    mutating func tick(at now: Date) -> Bool {
        guard running, seconds(at: now) <= 0 else { return false }
        if phase == .focus {
            completed += 1
            phase = completed % 4 == 0 ? .longBreak : .shortBreak
        } else { phase = .focus }
        remaining = phase.duration; running = false; deadline = nil; started = false
        return true
    }
    @discardableResult mutating func toggle(at now: Date) -> Bool {
        if tick(at: now) { return false }
        let voice = !running && !started && phase == .shortBreak
        if running { remaining = seconds(at: now); deadline = nil; running = false }
        else { deadline = now.addingTimeInterval(remaining); running = true; started = true }
        return voice
    }
    mutating func reset() { phase = .focus; remaining = 1500; running = false; started = false; deadline = nil }
    func snapshot(at now: Date) -> Pomodoro {
        var copy = self; copy.remaining = seconds(at: now); copy.running = false; copy.deadline = nil
        return copy
    }
    var valid: Bool { remaining > 0 && remaining <= phase.duration && completed >= 0 }
}
