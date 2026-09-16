import AppKit
import Foundation

final class PetPanel: NSPanel {
    override var canBecomeKey: Bool { false }
    override var canBecomeMain: Bool { false }
}
final class PetView: NSView {
    weak var controller: Companion?
    var image: NSImage?
    var caption = ""
    var dragStart: NSPoint?
    var windowStart = NSPoint.zero
    override var acceptsFirstResponder: Bool { false }
    override func draw(_ dirtyRect: NSRect) {
        NSColor.clear.setFill(); dirtyRect.fill(using: .copy)
        image?.draw(in: NSRect(x: 0, y: 28, width: bounds.width, height: bounds.height - 28), from: .zero, operation: .sourceOver, fraction: 1, respectFlipped: false, hints: [.interpolation:NSImageInterpolation.high])
        if !caption.isEmpty {
            let style = NSMutableParagraphStyle(); style.alignment = .center
            let font = NSFont.monospacedDigitSystemFont(ofSize: 13, weight: .medium)
            let size = (caption as NSString).size(withAttributes: [.font:font])
            let rect = NSRect(x:(bounds.width-size.width-24)/2, y:3, width:size.width+24, height:23)
            NSColor(calibratedRed:0.20,green:0.16,blue:0.12,alpha:0.82).setFill()
            NSBezierPath(roundedRect:rect,xRadius:11,yRadius:11).fill()
            (caption as NSString).draw(in:rect.insetBy(dx:8,dy:3), withAttributes:[.font:font,.foregroundColor:NSColor(calibratedRed:1,green:0.94,blue:0.81,alpha:1),.paragraphStyle:style])
        }
    }
    override func mouseDown(with event: NSEvent) {
        if event.modifierFlags.contains(.control) { rightMouseDown(with:event); return }
        dragStart = NSEvent.mouseLocation; windowStart = window?.frame.origin ?? .zero
    }
    override func mouseDragged(with event: NSEvent) {
        guard let start=dragStart else { return }
        let current=NSEvent.mouseLocation
        window?.setFrameOrigin(NSPoint(x:windowStart.x+current.x-start.x,y:windowStart.y+current.y-start.y))
    }
    override func mouseUp(with event:NSEvent) { controller?.keepOnScreen(); controller?.savePosition(); dragStart=nil }
    override func rightMouseDown(with event:NSEvent) {
        guard let menu=controller?.makeMenu() else {return}
        NSMenu.popUpContextMenu(menu,with:event,for:self)
    }
}

struct ClipInfo: Decodable { let frames:Int; let fps:Double }
struct StatusSnapshot: Decodable {
    let status: String?
    let lastUpdated: Double?
    let needsAttention: String?
}
final class Companion: NSObject, NSApplicationDelegate, NSMenuDelegate, NSSoundDelegate {
    let defaults=UserDefaults.standard
    let resources=Bundle.main.resourceURL!
    var panel:PetPanel!
    var pet:PetView!
    var statusItem:NSStatusItem!
    var clock:Timer?
    var model=Pomodoro()
    var mode=CompanionMode.codex
    var codexCelebration=Date.distantPast
    var clips:[String:ClipInfo]=[:]
    var clip="read", frame=0
    var nextFrame=Date.distantPast
    var celebration=Date.distantPast
    var lastSave=Date.distantPast
    var lastPoll=Date.distantPast
    var codex="unknown"
    var session=""
    var polling=false
    var sound:NSSound?
    var soundQueue:[String]=[]
    var muted=false
    var hidden=false
    var cache:[String:NSImage]=[:]
    var cacheOrder:[String]=[]
    var sourceURL:URL? {
        guard !session.isEmpty,session.allSatisfy({"0123456789abcdef-".contains($0)}) else{return nil}
        return FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".confirmo/claude-status/sessions/\(session).json")
    }
    func applicationDidFinishLaunching(_ notification:Notification) {
        // One companion instance; launching again brings the existing pet back through its menu.
        if NSRunningApplication.runningApplications(withBundleIdentifier:Bundle.main.bundleIdentifier!).count > 1 { NSApp.terminate(nil); return }
        muted=defaults.bool(forKey:"muted")
        mode=CompanionMode(rawValue:defaults.string(forKey:"mode") ?? "codex") ?? .codex
        if let data=defaults.data(forKey:"timer"), let saved=try? JSONDecoder().decode(Pomodoro.self,from:data),saved.valid { model=saved;model.running=false;model.deadline=nil }
        let arguments=ProcessInfo.processInfo.arguments
        if arguments.contains("--resume-after-update"),model.started {
            model.running=true;model.deadline=Date().addingTimeInterval(model.remaining)
        }
        if let index=arguments.firstIndex(of:"--session"),index+1<arguments.count { session=arguments[index+1];defaults.set(session,forKey:"session") }
        else {session=defaults.string(forKey:"session") ?? ""}
        if session.isEmpty,let data=try? Data(contentsOf:resources.appendingPathComponent("session.txt")),let value=String(data:data,encoding:.utf8) { session=value.trimmingCharacters(in:.whitespacesAndNewlines) }
        if let data=try? Data(contentsOf:resources.appendingPathComponent("Animations/manifest.json")),let values=try? JSONDecoder().decode([String:ClipInfo].self,from:data){clips=values}
        panel=PetPanel(contentRect:NSRect(x:0,y:0,width:216,height:328),styleMask:[.borderless,.nonactivatingPanel],backing:.buffered,defer:false)
        panel.title="钟离茶伴";panel.isOpaque=false;panel.backgroundColor = .clear;panel.hasShadow=false
        panel.level = .floating;panel.hidesOnDeactivate=false;panel.isReleasedWhenClosed=false
        panel.collectionBehavior=[.canJoinAllSpaces,.fullScreenAuxiliary,.stationary]
        pet=PetView(frame:NSRect(x:0,y:0,width:216,height:328));pet.controller=self;pet.toolTip="拖动移动 · 右键切换番茄钟 / Codex 陪伴"
        panel.contentView=pet
        let screen=NSScreen.main?.visibleFrame ?? NSRect(x:0,y:0,width:1280,height:800)
        let position=defaults.string(forKey:"position").map(NSPointFromString) ?? NSPoint(x:screen.maxX-260,y:screen.minY+35)
        panel.setFrameOrigin(position);keepOnScreen();panel.orderFrontRegardless()
        statusItem=NSStatusBar.system.statusItem(withLength:NSStatusItem.variableLength)
        statusItem.button?.title="茶";statusItem.button?.toolTip="钟离茶伴";refreshMenu()
        let timer=Timer(timeInterval:0.125,repeats:true){[weak self] _ in self?.update()}
        timer.tolerance=0.015;RunLoop.main.add(timer,forMode:.common);clock=timer
        update()
    }
    func keepOnScreen() {
        guard let panel=panel else{return}
        let center=NSPoint(x:panel.frame.midX,y:panel.frame.midY)
        let screen=NSScreen.screens.first(where:{$0.visibleFrame.contains(center)}) ?? NSScreen.main
        guard let rect=screen?.visibleFrame else{return}
        let x=min(max(panel.frame.minX,rect.minX),rect.maxX-panel.frame.width)
        let y=min(max(panel.frame.minY,rect.minY),rect.maxY-panel.frame.height)
        panel.setFrameOrigin(NSPoint(x:x,y:y))
    }
    func savePosition(){defaults.set(NSStringFromPoint(panel.frame.origin),forKey:"position")}
    func persist(){if let data=try? JSONEncoder().encode(model.snapshot(at:Date())){defaults.set(data,forKey:"timer")};lastSave=Date()}
    func applicationWillTerminate(_ notification:Notification){guard panel != nil else{return};persist();savePosition();clock?.invalidate();sound?.stop()}
    func pollStatus(_ now:Date) {
        guard !polling,now.timeIntervalSince(lastPoll)>=2 else{return}
        lastPoll=now;polling=true
        let url=sourceURL
        DispatchQueue.global(qos:.utility).async {[weak self] in
            var result="unknown"
            if let url=url,let attributes=try? FileManager.default.attributesOfItem(atPath:url.path),let size=attributes[.size] as? NSNumber,size.intValue<=65536,
               let data=try? Data(contentsOf:url),let parsed=try? JSONSerialization.jsonObject(with:data) as? [String:Any],
               let _=parsed["lastUpdated"] {
                result=codexStatus(parsed,now:Date())
            }
            let next=result
            DispatchQueue.main.async {
                guard let self=self else{return};self.polling=false
                if self.codex != next {
                    if next=="completed" && ["working","attention","error"].contains(self.codex) {self.codexCelebration=Date().addingTimeInterval(5)}
                    self.codex=next;self.refreshMenu()
                }
            }
        }
    }
    func update() {
        let now=Date()
        let wasFocus=model.phase == .focus
        if model.tick(at:now){if wasFocus{celebration=now.addingTimeInterval(6)};play("beeps.wav");persist();refreshMenu()}
        pollStatus(now)
        if model.running && now.timeIntervalSince(lastSave)>=30{persist()}
        var text=""
        if model.running || model.started {
            let seconds=Int(ceil(model.seconds(at:now)))
            text=String(format:"%@ %02d:%02d",model.running ? model.phase.name : "暂歇",seconds/60,seconds%60)
        } else if model.phase != .focus { text="歇一会 · 右键开始休息" }
        else if model.completed>0 && now<celebration { text="这一盏，敬你的专心" }
        if mode == .codex {text=""}
        if pet.caption != text {pet.caption=text;pet.needsDisplay=true}
        let desired=mode.action(running:model.running,started:model.started,timerCelebrating:now<celebration,codex:codex,codexCelebrating:now<codexCelebration)
        if desired != clip {clip=desired;frame=0;nextFrame = .distantPast}
        guard !hidden,now>=nextFrame,let spec=clips[clip],spec.frames>0 else{return}
        let key="\(clip)/\(String(format:"%04d",frame)).png"
        var picture=cache[key]
        if picture==nil {
            picture=NSImage(contentsOf:resources.appendingPathComponent("Animations/"+key))
            if let picture=picture {cache[key]=picture;cacheOrder.append(key)}
            while cacheOrder.count>4{cache.removeValue(forKey:cacheOrder.removeFirst())}
        }
        pet.image=picture;pet.needsDisplay=true
        frame=(frame+1)%spec.frames;nextFrame=now.addingTimeInterval(1/spec.fps)
    }
    func play(_ file:String){
        guard !muted else{return}
        if sound?.isPlaying == true {if soundQueue.count<2{soundQueue.append(file)};return}
        sound=NSSound(contentsOf:resources.appendingPathComponent(file),byReference:false)
        sound?.delegate=self;sound?.volume=0.6
        if sound?.play() != true {sound=nil}
    }
    func sound(_ finished:NSSound,didFinishPlaying success:Bool){
        DispatchQueue.main.async {[weak self] in
            guard let self=self,self.sound === finished else{return}
            self.sound=nil
            if !self.soundQueue.isEmpty {self.play(self.soundQueue.removeFirst())}
        }
    }
    func makeMenu()->NSMenu {
        let menu=NSMenu();menu.delegate=self
        func item(_ title:String,_ action:Selector?)->NSMenuItem {let it=NSMenuItem(title:title,action:action,keyEquivalent:"");it.target=self;menu.addItem(it);return it}
        let pomo=item("番茄钟模式",#selector(selectMode(_:)));pomo.representedObject="pomodoro";pomo.state=mode == .pomodoro ? .on : .off
        let companion=item("Codex 陪伴模式",#selector(selectMode(_:)));companion.representedObject="codex";companion.state=mode == .codex ? .on : .off
        menu.addItem(.separator())
        if mode == .pomodoro {
            let actionTitle=model.running ? "暂停" : model.started ? "继续\(model.phase.name)" : model.phase == .focus ? "开始 25 分钟专注" : "开始 \(Int(model.phase.duration/60)) 分钟休息"
            _=item(actionTitle,#selector(toggle))
            if model.running || model.started || model.phase != .focus {_=item("结束本轮",#selector(reset))}
        } else {
            let label:[String:String]=["working":"正在工作","completed":"本轮回复完成","attention":"需要你处理","error":"发生错误","idle":"等待任务","unknown":"状态暂不可用"]
            _=item("Codex：\(label[codex] ?? "状态暂不可用")",nil)
            _=item("关注任务：\(session.suffix(8))",nil)
            if model.running {_=item("番茄钟正在后台计时",nil)}
        }
        menu.addItem(.separator())
        let mute=item("静音",#selector(mute));mute.state=muted ? .on : .off
        _=item(hidden ? "显示钟离" : "暂时隐藏",#selector(hidePet))
        menu.addItem(.separator());_=item("退出钟离茶伴",#selector(quit))
        return menu
    }
    func refreshMenu(){statusItem?.menu=makeMenu()}
    @objc func selectMode(_ sender:NSMenuItem){guard let value=sender.representedObject as? String,let next=CompanionMode(rawValue:value) else{return};mode=next;defaults.set(mode.rawValue,forKey:"mode");refreshMenu();update()}
    @objc func toggle(){if model.running && model.seconds(at:Date())<=0 {update();return};if model.toggle(at:Date()){play("break-voice.mp3")};celebration = .distantPast;persist();refreshMenu();update()}
    @objc func reset(){model.reset();celebration = .distantPast;persist();refreshMenu();update()}
    @objc func mute(){muted.toggle();defaults.set(muted,forKey:"muted");if muted{soundQueue=[];sound?.stop();sound=nil};refreshMenu()}
    @objc func hidePet(){hidden.toggle();if hidden{panel.orderOut(nil)}else{panel.orderFrontRegardless()};refreshMenu()}
    @objc func quit(){NSApp.terminate(nil)}
}
let app=NSApplication.shared
app.setActivationPolicy(.accessory)
let companion=Companion();app.delegate=companion
app.run()
