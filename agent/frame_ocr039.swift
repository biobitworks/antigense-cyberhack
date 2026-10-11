import Foundation
import Vision
import AppKit
var out:[[String:Any]]=[]
for path in CommandLine.arguments.dropFirst(){
 let url=URL(fileURLWithPath:path)
 let req=VNRecognizeTextRequest()
 req.recognitionLevel = .accurate
 req.usesLanguageCorrection = false
 do {
  try VNImageRequestHandler(url:url,options:[:]).perform([req])
  let lines=(req.results ?? []).compactMap{$0.topCandidates(1).first?.string}
  out.append(["file":url.lastPathComponent,"lines":lines])
 } catch {out.append(["file":url.lastPathComponent,"error":String(describing:error)])}
}
let data=try JSONSerialization.data(withJSONObject:out,options:[.sortedKeys])
print(String(data:data,encoding:.utf8)!)
