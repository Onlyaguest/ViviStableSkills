import AppKit
let root=URL(fileURLWithPath:CommandLine.arguments[1])
var manifest:[String:[String:Int]]=[:]
for action in ["read","doze","happy","piqued"] {
 let dir=root.appendingPathComponent("Animations/\(action)")
 try FileManager.default.createDirectory(at:dir,withIntermediateDirectories:true)
 let image=NSImage(size:NSSize(width:288,height:400))
 image.lockFocus()
 NSColor(calibratedRed:0.65,green:0.48,blue:0.23,alpha:1).setFill()
 NSBezierPath(roundedRect:NSRect(x:44,y:70,width:180,height:180),xRadius:40,yRadius:40).fill()
 let text=["read":"专注","doze":"等待","happy":"完成","piqued":"留意"][action]!
 (text as NSString).draw(at:NSPoint(x:96,y:140),withAttributes:[.font:NSFont.systemFont(ofSize:26),.foregroundColor:NSColor.white])
 image.unlockFocus()
 let bitmap=NSBitmapImageRep(data:image.tiffRepresentation!)!
 try bitmap.representation(using:.png,properties:[:])!.write(to:dir.appendingPathComponent("0000.png"))
 manifest[action] = ["frames":1,"fps":8,"width":288,"height":400]
}
try JSONSerialization.data(withJSONObject:manifest).write(to:root.appendingPathComponent("Animations/manifest.json"))
