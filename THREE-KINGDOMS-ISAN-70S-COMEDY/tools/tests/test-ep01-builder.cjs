'use strict';
const assert=require('node:assert/strict');
const zlib=require('node:zlib');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
if(!globalThis.crypto || !globalThis.crypto.subtle)Object.defineProperty(globalThis,'crypto',{value:require('node:crypto').webcrypto,configurable:true});
const A=require('../ep01-builder.js');
// Small generated parser fixtures only. They are not production character images.
function png(r,g,b){const head=Buffer.alloc(13);head.writeUInt32BE(1,0);head.writeUInt32BE(1,4);head[8]=8;head[9]=2;function chunk(t,v){const type=Buffer.from(t),n=Buffer.alloc(4),crc=Buffer.alloc(4);n.writeUInt32BE(v.length);crc.writeUInt32BE(A.crc32(Buffer.concat([type,v])));return Buffer.concat([n,type,v,crc]);}return 'data:image/png;base64,'+Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',head),chunk('IDAT',zlib.deflateSync(Buffer.from([0,r,g,b]))),chunk('IEND',Buffer.alloc(0))]).toString('base64');}
async function main(){
 const html=fs.readFileSync(path.join(__dirname,'../BUILD_EP01_FROM_EXPORT.html'),'utf8');
 for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi))if(match[1].trim())new vm.Script(match[1]);
 const pics=[png(10,20,30),png(40,50,60),png(70,80,90),png(100,110,120)];
 const source={projectId:'three-kingdoms-isan-70s-comedy-ep01',settings:{visualStyle:'KEEP EXACT 1970s source style',customVisualStyle:'KEEP CUSTOM',customCharacterStyle:'KEEP APPROVED CHARACTER STYLE',aspectRatio:'9:16'},movie:{genre:'Retro Comedy',characters:A.IDS.map((id,i)=>({id,name:A.NAMES[id],mainOutfit:'EXACT SOURCE OUTFIT '+id,imageBase64:pics[i],imageStatus:'complete',imageMediaId:'STALE_ID'})),scenes:[{id:'old-scene',order:1,title:'old',sceneCharacters:A.IDS.map(id=>({id})),imageBase64:pics[0],videoBase64:'DO_NOT_COPY',videoMediaId:'OLD_VIDEO'}],atmosphereAssets:[{id:'garden',title:'Garden',imageBase64:pics[3],status:'complete'}]}};
 const original=JSON.stringify(source),selections={};
 A.IDS.forEach(id=>{selections[id]={...A.candidates(source,id)[0],confirmed:true};});selections.location={...A.candidates(source,'location')[0],confirmed:true};
 const built=await A.build(source,selections,{sourceFileName:'fixture.json'});
 assert.equal(JSON.stringify(source),original,'original must not be mutated');
 assert.equal(built.project.currentStep,6);assert.equal(built.project.movie.characters.length,3);assert.equal(built.project.movie.scenes.length,6);assert.equal(built.project.settings.customLocationCount,1);
 assert.equal(built.project.settings.visualStyle,source.settings.visualStyle);
 for(let i=0;i<3;i++){const c=built.project.movie.characters[i];assert.equal(c.imageBase64,pics[i]);assert.equal(c.mainOutfit,source.movie.characters[i].mainOutfit);assert.equal(c.imageMediaId,undefined);assert.equal(c.imageStatus,'complete');assert.equal(c.referenceImageHash,await A.sha256(A.parseImage(pics[i]).bytes));}
 for(let i=0;i<6;i++){const s=built.project.movie.scenes[i];assert.equal(s.duration,6);assert.equal(s.dialogues.length,1);assert.ok(s.videoPrompt.includes(s.dialogues[0].text));assert.equal(s.videoBase64,undefined);assert.equal(s.imageBase64,undefined);if(i)assert.equal(s.continuityStartState,built.project.movie.scenes[i-1].continuityEndFrame);}
 const duplicate={...selections,'guan-yu':selections['liu-bei']};await assert.rejects(A.build(source,duplicate),/ซ้ำกัน/);
 const missing={...selections};delete missing['liu-bei'];await assert.rejects(A.build(source,missing),/ยืนยัน/);
 await assert.rejects(A.build(source,{...selections,'zhang-fei':{...selections['zhang-fei'],native:false,crop:null}}),/ครอป/);
 assert.throws(()=>A.parseImage('data:image/png;base64,...'),/Base64/);assert.throws(()=>A.assertSource({...source,projectId:'other'}),/โปรเจกต์/);
 assert.throws(()=>A.parseImage('https://example.invalid/image.png'),/Base64/);
 const files=A.packageFiles(built);assert.equal(files.length,13);assert.equal(new Set(files.map(f=>f.name)).size,13);
 const step6=JSON.parse(new TextDecoder().decode(files.find(f=>f.name.endsWith('/STEP6.json')).data));const step5=JSON.parse(new TextDecoder().decode(files.find(f=>f.name.endsWith('/STEP5.json')).data));assert.equal(step5.currentStep,5);assert.deepEqual(step5.movie.characters,step6.movie.characters);
 const zip=Buffer.concat(A.makeZip(files).map(x=>Buffer.from(x)));assert.equal(zip.readUInt32LE(0),0x04034b50);assert.equal(zip.readUInt32LE(zip.length-22),0x06054b50);assert.equal(zip.readUInt16LE(zip.length-12),files.length);
 let pos=0;for(const file of files){assert.equal(zip.readUInt32LE(pos),0x04034b50);const n=zip.readUInt16LE(pos+26),size=zip.readUInt32LE(pos+18),data=zip.subarray(pos+30+n,pos+30+n+size);assert.equal(zip.subarray(pos+30,pos+30+n).toString(),file.name);assert.equal(zip.readUInt32LE(pos+14),A.crc32(data));assert.deepEqual(data,Buffer.from(file.data));pos+=30+n+size;}
 assert.equal(built.project.buildAudit.actualToolImportTested,false);assert.equal(built.qa.guaranteedIdentityMatch,false);
 console.log('PASS: source preserved, exact assets and style, native project shape, 6 scenes/36s/one location, speaker refs, continuity, stale-media removal, rejection gates, STEP5 parity, ZIP CRC and browser script syntax. Real P&P import and visual generation are NOT tested.');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
