import AppKit
import Foundation
let output=CommandLine.arguments[1], text=CommandLine.arguments[2]
let image=NSImage(size:NSSize(width:1150,height:32))
image.lockFocus()
NSColor(calibratedWhite:0,alpha:0.9).setFill()
NSRect(x:0,y:0,width:1150,height:32).fill()
let attrs:[NSAttributedString.Key:Any] = [.font:NSFont.monospacedSystemFont(ofSize:13,weight:.medium),.foregroundColor:NSColor.white]
(text as NSString).draw(at:NSPoint(x:8,y:8),withAttributes:attrs)
image.unlockFocus()
let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:output))
