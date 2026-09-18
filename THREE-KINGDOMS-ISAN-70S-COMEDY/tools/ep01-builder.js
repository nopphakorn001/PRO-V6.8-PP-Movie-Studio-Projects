/* Offline EP01 assembler. No network calls, image generation, or image retouching. */
(function (root) {
  'use strict';
  const SERIES = 'THREE-KINGDOMS-ISAN-70S-COMEDY';
  const EP = 'EP01-Peach-Garden-Oath';
  const LOCATION = 'ร้านเหล้าริมสวนท้อ';
  const IDS = ['liu-bei', 'guan-yu', 'zhang-fei'];
  const NAMES = {'liu-bei':'เล่าปี่','guan-yu':'กวนอู','zhang-fei':'เตียวหุย'};
  const NICKS = {'liu-bei':'พี่เล่า','guan-yu':'พี่กวน','zhang-fei':'เจ้าเตียว'};
  const STYLE_KEYS = ['visualStyle','customVisualStyle','customCharacterStyle','visualStyleId','characterStyleCategory','selectedProjectStyle','selectedProjectType'];
  const VOICES = {
    'liu-bei':'Adult middle-aged male, gentle slightly weary voice, clear informal Thai period-comedy delivery.',
    'guan-yu':'Adult middle-aged male, low dry resonant voice, restrained deadpan Thai period-comedy delivery.',
    'zhang-fei':'Adult middle-aged male, rough booming voice, boastful rustic comic delivery, intelligible Thai period speech rather than slurring.'
  };
  const SCENES = [
    {title:'รองเท้าขายมิออก',speaker:'liu-bei',text:'เฮ้อ...รองเท้าข้าขายมิได้สักคู่',action:'Liu Bei lifts one straw sandal from beside his seat and sighs. Guan Yu and Zhang Fei remain at the same table, listening silently.',framing:'Medium-close shot of Liu Bei; retain the table edge and part of his companions at the frame edges.',end:'Liu Bei has placed the sandal back beside his seat. All three remain seated in their established places. Zhang Fei holds the small jar beside the table.'},
    {title:'เจ้าเตียวชวนพัก',speaker:'zhang-fei',text:'พี่เล่า! หน้าหมองอยู่ใย มาซดสุราก่อน!',action:'Zhang Fei places his clay jar on the same table while inviting Liu Bei to rest. The other two react without speaking.',framing:'Medium-close shot of Zhang Fei addressing Liu Bei; do not change his outfit or move the table.',end:'The jar rests at the center of the same table. All three are still seated. Guan Yu has one hand next to his own clay cup.'},
    {title:'พี่กวนหูดี',speaker:'guan-yu',text:'เจ้าเตียว...ข้าได้ยินคำว่าสุราแต่ไกล',action:'Guan Yu slides his clay cup a short distance toward the jar with a completely serious expression. He is not walking in from another location.',framing:'Medium-close shot of Guan Yu with the same jar and tabletop visible below him.',end:'Guan Yu has slid his cup toward the jar. The jar stays in place. All three remain seated at the original table. Liu Bei rests a hand beside his own cup.'},
    {title:'สาบานที่โต๊ะเดิม',speaker:'liu-bei',text:'พี่กวน เจ้าเตียว...จากนี้อย่าทิ้งกันยามยาก',action:'Liu Bei raises his own clay cup a little to propose brotherhood. Guan Yu and Zhang Fei acknowledge him with silent looks. Everyone stays seated.',framing:'Medium three-shot on the same side of the table axis. Liu Bei is the only speaking face.',end:'Liu Bei holds his cup raised at chest height. Guan Yu and Zhang Fei remain seated with their cups on the table. The jar remains centered; the sandals remain beside Liu Bei.'},
    {title:'พี่น้องก็ต้องหาร',speaker:'zhang-fei',text:'ร่วมเป็นร่วมตาย! แต่ค่าสุรา...หารสามนะ!',action:'Zhang Fei turns his empty cloth pouch inside out over the table. Liu Bei lowers his cup onto its original spot; the others react silently. No new proprietor enters.',framing:'Medium shot favoring Zhang Fei; the empty pouch is readable through action, not on-screen writing.',end:'Zhang Fei holds his empty pouch open. Liu Bei has returned his cup to its original position. Guan Yu touches his own pouch. Nobody has left the table.'},
    {title:'มีแต่ใจ',speaker:'guan-yu',text:'พี่เล่า...ข้ามีแต่ใจ เอาจ่ายแทนได้หรือไม่?',action:'Guan Yu shows his own empty pouch and delivers the final deadpan line. Liu Bei glances at both empty pouches, then at his unsold sandals. Hold their embarrassed silent reaction to finish the joke.',framing:'Medium three-shot of the original table. End on a short reaction hold; no walk-away, new setting, or extra actor.',end:'All three remain at the same table with empty pouches, unchanged cups and jar. The unpaid bill joke is resolved by their embarrassed reaction; the episode ends here.'}
  ];
  const copy = x => JSON.parse(JSON.stringify(x));
  function requireValue(ok, message) { if (!ok) throw new Error(message); }
  function isDataUri(v) { return typeof v === 'string' && /^data:image\/(png|jpe?g|webp);base64,/i.test(v); }
  function bytesFromBase64(s) {
    if (typeof Buffer !== 'undefined') return new Uint8Array(Buffer.from(s, 'base64'));
    const b = atob(s); return Uint8Array.from(b, c => c.charCodeAt(0));
  }
  function parseImage(uri) {
    requireValue(isDataUri(uri), 'ต้องเป็นภาพ PNG/JPEG/WebP ที่ฝัง Base64 จริง ไม่ใช่ URL หรือ placeholder');
    const at = uri.indexOf(',');
    const encoded = uri.slice(at + 1).replace(/\s/g, '');
    requireValue(encoded.length > 0 && encoded.length % 4 === 0 && /^[A-Za-z0-9+/]+={0,2}$/.test(encoded), 'Base64 ภาพไม่สมบูรณ์');
    const bytes = bytesFromBase64(encoded);
    const mime = uri.slice(5, at).split(';')[0].toLowerCase().replace('image/jpg','image/jpeg');
    const png = bytes.length > 24 && bytes[0] === 137 && bytes[1] === 80 && bytes[2] === 78 && bytes[3] === 71;
    const jpeg = bytes.length > 4 && bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
    const webp = bytes.length > 12 && String.fromCharCode(...bytes.slice(0,4)) === 'RIFF' && String.fromCharCode(...bytes.slice(8,12)) === 'WEBP';
    requireValue((mime === 'image/png' && png) || (mime === 'image/jpeg' && jpeg) || (mime === 'image/webp' && webp), 'ชนิดภาพไม่ตรงกับข้อมูล Base64');
    return {bytes, mime, encoded, extension: mime === 'image/jpeg' ? 'jpg' : mime.split('/')[1]};
  }
  async function sha256(bytes) {
    requireValue(root.crypto && root.crypto.subtle, 'เบราว์เซอร์นี้ไม่มี SHA-256 สำหรับตรวจภาพ กรุณาเปิดไฟล์ HTML ด้วย Chrome/Edge บนเครื่อง');
    const digest = await root.crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(digest), v => v.toString(16).padStart(2,'0')).join('');
  }
  function assertSource(source) {
    requireValue(source && source.projectId === 'three-kingdoms-isan-70s-comedy-ep01', 'เลือก JSON export ต้นฉบับ EP01 สามก๊กบ้านเฮา ไม่ใช่โปรเจกต์อื่นหรือภาพโปสเตอร์');
    requireValue(source.settings && source.movie && Array.isArray(source.movie.scenes) && Array.isArray(source.movie.characters), 'ไฟล์ต้องใช้โครง settings + movie.scenes + movie.characters');
    requireValue(typeof source.settings.visualStyle === 'string' && source.settings.visualStyle.length > 0, 'ไฟล์ไม่มี visualStyle ต้นฉบับ');
    for (const id of IDS) requireValue(source.movie.characters.some(c => c.id === id), 'ไม่พบ character id เดิม: ' + id);
  }
  function embeddedIn(record, prefix) {
    const out = [], seen = new Set();
    function visit(value, path, depth) {
      if (depth > 5 || value == null) return;
      if (isDataUri(value)) {
        if (!seen.has(value)) { seen.add(value); out.push({dataUri:value,sourcePath:path}); }
        return;
      }
      if (typeof value !== 'object') return;
      for (const [key, item] of Object.entries(value)) {
        if (/video|history|generations/i.test(key)) continue;
        const next = path + '.' + key;
        if (typeof item === 'string' && /^(imageBase64|base64|data)$/i.test(key) && !item.startsWith('data:')) {
          const mime = value.mimeType || value.imageMimeType || record.imageMimeType;
          if (/^image\/(png|jpe?g|webp)$/i.test(mime || '') && /^[A-Za-z0-9+/\s]+={0,2}$/.test(item)) visit('data:' + mime + ';base64,' + item, next, depth + 1);
        } else visit(item, next, depth + 1);
      }
    }
    visit(record, prefix, 0); return out;
  }
  function candidates(source, id) {
    assertSource(source);
    const out = [];
    if (IDS.includes(id)) {
      const record = source.movie.characters.find(c => c.id === id);
      embeddedIn(record, 'movie.characters.' + id).forEach(x => out.push({...x,recordId:id,kind:'character',native:true,label:'ภาพ STEP5 เดิม — ' + NAMES[id]}));
    } else {
      for (const record of source.movie.atmosphereAssets || []) embeddedIn(record,'movie.atmosphereAssets.' + record.id).forEach(x => out.push({...x,recordId:record.id,kind:'location',native:true,label:'สถานที่เดิม — ' + (record.title || record.id)}));
    }
    for (const scene of source.movie.scenes) {
      if (IDS.includes(id) && !(scene.sceneCharacters || []).some(c => c.id === id)) continue;
      for (const item of embeddedIn({imageBase64:scene.imageBase64,imageUrl:scene.imageUrl,image:scene.image,imageMimeType:scene.imageMimeType}, 'movie.scenes.' + scene.id)) {
        out.push({...item,recordId:scene.id,kind:'scene',native:false,label:'ภาพฉาก ' + scene.order + ' — ' + scene.title});
      }
    }
    return out;
  }
  // Remove source-project runtime media links; never reuse rendered scene videos as a new result.
  function clean(record) {
    const out = {};
    for (const [key,value] of Object.entries(record || {})) {
      if (/mediaId$|^video|^imageHistory$|^generationHistory$|^isGenerating|^generationProgress$|^selectedImage/i.test(key)) continue;
      if (/^image(Base64|Url|Data|MimeType)?$|^referenceImage(Base64|Hash|Url)?$|^generatedImage(Url)?$/i.test(key)) continue;
      out[key] = copy(value);
    }
    return out;
  }
  function nativeStatus(source) {
    const candidate = source.movie.characters.find(c => embeddedIn(c,'').length && c.imageStatus && !/idle|pending|error|loading|generating/i.test(c.imageStatus));
    return candidate ? candidate.imageStatus : 'done';
  }
  async function build(source, selected, info = {}) {
    assertSource(source);
    const assets = {};
    for (const id of [...IDS,'location']) {
      const item = selected[id];
      requireValue(item && item.confirmed === true && isDataUri(item.dataUri), 'ยังไม่ได้ยืนยันภาพต้นฉบับ: ' + (NAMES[id] || LOCATION));
      requireValue(id === 'location' || item.native === true || item.crop != null, 'ภาพฉากที่มีตัวละครต้องครอปให้เหลือคนที่ต้องการก่อน: ' + NAMES[id]);
      const parsed = parseImage(item.dataUri);
      assets[id] = {...parsed,dataUri:item.dataUri,sha256:await sha256(parsed.bytes),sourcePath:item.sourcePath,sourceRecordId:item.recordId,kind:item.kind,crop:item.crop || null,native:!!item.native};
    }
    requireValue(new Set(IDS.map(id => assets[id].sha256)).size === 3, 'ภาพสามตัวละครซ้ำกัน ห้ามใช้ภาพกลุ่มใบเดียวเป็น Master ของทุกคน');
    const originalStatusAvailable = source.movie.characters.some(c => embeddedIn(c,'').length && c.imageStatus && !/idle|pending|error|loading|generating/i.test(c.imageStatus));
    const chars = IDS.map(id => {
      const original = source.movie.characters.find(c => c.id === id), a = assets[id];
      const c = clean(original);
      c.id = id; c.name = NAMES[id]; c.nickname = NICKS[id];
      // Keep the native object shape. These direct data-URI fields are intentionally redundant;
      // the actual third-party importer still needs a Step5 thumbnail check.
      c.imageBase64 = a.dataUri; c.imageUrl = a.dataUri; c.imageMimeType = a.mime;
      if (Object.prototype.hasOwnProperty.call(original,'image') && (typeof original.image === 'string' || original.image == null)) c.image = a.dataUri;
      if (original.referenceImage && typeof original.referenceImage === 'object') c.referenceImage = {dataUri:a.dataUri,mimeType:a.mime,sha256:a.sha256};
      c.imageStatus = nativeStatus(source);
      c.characterReferenceId = id + '-approved-' + a.sha256.slice(0,12);
      c.identityLocked = true; c.faceLocked = true; c.costumeLocked = true;
      c.voiceProfile = {...(typeof original.voiceProfile === 'object' && original.voiceProfile || {}),tonePrompt:VOICES[id] + ' Only speak the assigned Thai line. Never speak other characters\' lines.'};
      c.referenceImageHash = a.sha256;
      c.referenceProvenance = {sourceFileName:info.sourceFileName || null,sourceFileSha256:info.sourceFileSha256 || null,sourcePath:a.sourcePath,sourceRecordId:a.sourceRecordId,transformation:a.crop ? 'CROP_ONLY_NO_RESYNTHESIS':'NONE',crop:a.crop};
      return c;
    });
    const allRefs = chars.map(c => ({id:c.id,name:c.name}));
    const start = 'All three approved characters are already seated at one rough wooden table beneath the peach tree beside the tavern. Maintain their seating positions established in the first generated image. Liu Bei holds one unsold straw sandal; the small clay jar is beside Zhang Fei. Three cups are present. Same dry afternoon, clothes and light for the entire episode.';
    const style = source.settings.visualStyle + ' ' + (source.settings.customVisualStyle || '');
    const nativePrompt = 'Use the supplied STEP5 reference images for the exact approved faces, hair, facial hair, body proportions and outfits. Do not beautify, redesign, substitute an actor or imitate the earlier poster. Use the selected location image only for the same background geometry. One tavern table, one peach tree, one continuous afternoon. No POV/bodycam style, montage, modern objects or second location. ';
    const scenes = SCENES.map((s,i) => {
      const id = 'isan-ep01-master-v3-' + String(i+1).padStart(3,'0');
      return {
        id,order:i+1,title:s.title,description:s.action,location:LOCATION,mood:'rustic dry comedy',
        sceneCharacters:copy(allRefs),isDetailed:true,duration:6,
        script:NAMES[s.speaker] + ': ' + s.text,
        dialogues:[{characterId:s.speaker,speakerName:NAMES[s.speaker],text:s.text}],
        isGenerating:false,generationProgress:0,isGeneratingImage:false,isGeneratingVideo:false,
        narrationText:'',
        imageDescription:nativePrompt + style + ' Starting state: ' + (i ? SCENES[i-1].end : start) + ' Composition: ' + s.framing + ' Single scene frame, no labels, captions or storyboard panels.',
        actionDescription:s.action,
        videoPrompt:nativePrompt + style + ' ' + s.framing + ' ' + s.action + ' Only ' + NAMES[s.speaker] + ' (' + s.speaker + ') speaks. Thai period-style dialogue, exactly once: "' + s.text + '". ' + VOICES[s.speaker] + ' Allow a short silent setup, finish the line before the final second, and hold a silent reaction. The other two do not move their lips to the dialogue. No narrator, overlapping speech, added words, music or canned laughter. Low leaf rustle, cloth movement and clay-cup sounds only. Preserve the same people and props. End state: ' + s.end,
        audioDirection:'Thai character dialogue only as assigned; one speaker. Quiet location ambience beneath speech; no background conversation, narrator, music or laughter track.',
        locationRef:'loc-ep01-peach-tavern',
        previousSceneReference:i ? 'isan-ep01-master-v3-' + String(i).padStart(3,'0') : null,
        continuityStartState:i ? SCENES[i-1].end : start,
        continuityEndFrame:s.end,
        referenceUsageNote:'Select the STEP5 images in the actual tool. From Scene 2 also attach the approved previous end-frame when the tool supports it. JSON metadata alone does not attach images or enforce identity.'
      };
    });
    const locationOriginal = (source.movie.atmosphereAssets || []).find(x => x.id === assets.location.sourceRecordId) || {};
    const location = {
      ...clean(locationOriginal),id:'loc-ep01-peach-tavern',title:LOCATION,
      description:'The single approved peach-tree tavern tabletop location. Preserve geometry from its reference image; all six shots are angles of this same table. Do not create a separate market, another garden, exit journey or second establishment.',
      imageBase64:assets.location.dataUri,imageUrl:assets.location.dataUri,imageMimeType:assets.location.mime,
      status:locationOriginal.status && !/idle|pending|error|loading|generating/i.test(locationOriginal.status) ? locationOriginal.status : nativeStatus(source),
      relatedScenes:scenes.map(s => s.id),lighting:'Unchanged natural afternoon lighting and the exact source vintage film treatment.',
      continuityRules:'Same table, tree, jar, three cups and actor seating; only the current action changes their state.',
      referenceImageHash:assets.location.sha256
    };
    const settings = {...copy(source.settings),aspectRatio:'9:16',language:'Thai',targetSceneCount:6,secondsPerScene:6,castingMode:'custom',customCastingCount:3,locationMode:'custom',customLocationCount:1,voiceEnabled:true,narrationEnabled:false,dialogueEnabled:true,musicEnabled:false,voiceGender:'male',voiceStyle:'ไทยย้อนยุคแบบหนังตลก พูดสั้น ใช้ข้า เจ้า อยู่ใย มิได้ และชื่อเรียกพี่เล่า พี่กวน เจ้าเตียว ไม่ใช่ราชาศัพท์',voiceStyleId:'custom',identityMode:'APPROVED_EMBEDDED_REFERENCE_IMAGES',characterImagePolicy:'REUSE_APPROVED_IMAGES_NO_REGENERATION',speakerNicknameMap:copy(NICKS),customProjectStructure:'Six connected scenes of six seconds each, one tavern table only. All three STEP5 characters have embedded approved source images. One visible speaker per clip. Keep the original 1970s style exactly. Reference selection must be checked in the actual generation tool.'};
    const project = {
      projectId:'three-kingdoms-isan-70s-comedy-ep01-approved-master-v3',settings,
      movie:{genre:source.movie.genre,selectedGenres:copy(source.movie.selectedGenres || []),selectedVisualMoods:copy(source.movie.selectedVisualMoods || []),
        storyTitle:'สามก๊กบ้านเฮา EP01 — สาบานได้ แต่ใครจ่ายสุรา',
        plotDetails:'Fictional rustic comic adaptation of the Three Kingdoms characters, not an assertion of historical dialogue or footage.',
        mainStoryPrompt:nativePrompt + style + ' A complete 36-second joke at one table: Liu Bei complains about unsold sandals; Zhang Fei invites him to rest; Guan Yu jokes about hearing the word wine; they pledge brotherhood; splitting the cost exposes their empty pouches; Guan Yu offers his heart instead of money. Use informal Thai period dialogue with พี่เล่า, พี่กวน and เจ้าเตียว. No new character or location.',
        storySummary:'ทั้งสามนั่งโต๊ะเดียวกันที่ร้านเหล้าริมสวนท้อ เล่าปี่ขายรองเท้าไม่ออก เจ้าเตียวชวนดื่ม พี่กวนสวนมุกหน้าตาย ก่อนสาบานเป็นพี่น้อง แต่พอหารค่าสุรา ทุกคนกลับมีแต่ใจ ไม่มีเงิน เรื่องจบด้วยสีหน้าอึดอัดของทั้งสามที่โต๊ะเดิม',
        genreDetailPrompt:source.movie.genreDetailPrompt || '',characters:chars,atmosphereAssets:[location],productAssets:[],scenes,customGenre:source.movie.customGenre || 'Three Kingdoms Isan 1970s Vertical Comedy',productionDesignAnalyzed:true},
      currentStep:6,revision:'EP01_APPROVED_ASSETS_ONE_LOCATION_V3',
      buildAudit:{sourceFileName:info.sourceFileName || null,sourceFileSha256:info.sourceFileSha256 || null,sourceProjectId:source.projectId,stylePreserved:true,masterImagesEmbedded:true,sceneRendersReused:false,actualToolImportTested:false,automaticReferenceSelectionVerified:false,imageStatusValueInferred:!originalStatusAvailable,generatedAt:new Date().toISOString()}
    };
    const checked = validate(project,source,assets);
    const lock = {
      series:SERIES,version:'3.0',scope:'Future episodes built from this approved master pack',
      sourcePolicy:'Reuse these exact images and stable character IDs. Do not regenerate a face or replace a master silently.',
      styleLock:Object.fromEntries(STYLE_KEYS.filter(k => k in source.settings).map(k => [k,copy(source.settings[k])])),
      dialogueStyle:'Short informal Thai period comedy; one visible speaker per scene; canonical names retained in IDs and speakerName.',nicknames:copy(NICKS),
      locationPolicy:'ONE_PHYSICAL_LOCATION_PER_EPISODE',
      referencePriority:['approved_character_images','approved_previous_end_frame','episode_location_image','current_action'],
      enforcement:'These are authoring instructions and reference assets, not code inside the third-party generator. Image matching, lip-sync and automatic chaining still require output review.',
      femaleArchetypePolicy:'Future approved female Three Kingdoms characters may be bold and sharp-tongued, but no unapproved new character, modern clothes or changed series style in this episode.'
    };
    const master = {series:SERIES,version:'3.0',status:'APPROVED_SOURCE_IMAGES_EMBEDDED',characters:copy(chars),styleLock:copy(lock.styleLock),sourceFileSha256:info.sourceFileSha256 || null,usage:'Copy the same movie.characters records into later episode imports. The byte hashes must match this version. Do not regenerate.'};
    return {project,assets,master,lock,location,qa:checked};
  }
  function validate(project, source, assets) {
    const scenes = project.movie.scenes;
    requireValue(project.currentStep === 6 && scenes.length === 6,'STEP6/scene count mismatch');
    requireValue(scenes.reduce((n,s) => n+s.duration,0) === 36,'Episode duration must equal 36 seconds');
    requireValue(new Set(scenes.map(s => s.id)).size === 6,'Duplicate scene IDs');
    requireValue(new Set(scenes.map(s => s.location)).size === 1 && project.movie.atmosphereAssets.length === 1,'An episode must use one location');
    for (const key of STYLE_KEYS) requireValue(JSON.stringify(project.settings[key]) === JSON.stringify(source.settings[key]),'Style changed: ' + key);
    for (const c of project.movie.characters) {
      requireValue(c.referenceImageHash === assets[c.id].sha256,'Character image hash mismatch');
      requireValue(c.imageBase64 === assets[c.id].dataUri,'Embedded image differs from selected reference');
      parseImage(c.imageBase64);
    }
    for (let i=0;i<scenes.length;i++) {
      const s = scenes[i];
      requireValue(s.dialogues.length === 1 && IDS.includes(s.dialogues[0].characterId),'Invalid speaker');
      requireValue(s.script === s.dialogues[0].speakerName + ': ' + s.dialogues[0].text,'Script/dialogue mismatch');
      requireValue(s.videoPrompt.includes(s.dialogues[0].text),'Dialogue missing from actual video prompt');
      requireValue(!s.imageBase64 && !s.videoBase64 && !s.videoMediaId && !s.imageMediaId,'Old render leaked into new scenes');
      requireValue(s.sceneCharacters.every(c => IDS.includes(c.id)),'Dangling character reference');
      if (i) requireValue(s.continuityStartState === scenes[i-1].continuityEndFrame,'Continuity chain broken');
    }
    return {structuralValidation:'PASS',scenes:6,durationSeconds:36,characters:3,locations:1,dialogueCount:6,masterImageCount:3,sourceStyleStrings:'EXACT_MATCH',sceneMediaCleared:true,actualImportTested:false,actualVideoRendered:false,guaranteedIdentityMatch:false,warnings:['Confirm all STEP5 thumbnails after import. Additional JSON locks are not automatic enforcement.','If the export lacks a populated native character image field, imageBase64/imageUrl binding is a compatibility attempt and must be checked in the real tool.','Character images constrain visuals, not a persistent synthesized voice ID.']};
  }
  function packageFiles(result) {
    const files = [];
    const json = (name,value) => files.push({name:SERIES+'/'+name,data:new TextEncoder().encode(JSON.stringify(value,null,2)+'\n')});
    json(EP+'/STEP6.json',result.project);
    const step5 = copy(result.project); step5.currentStep=5; json(EP+'/STEP5.json',step5);
    json('CHARACTER_MASTER.json',result.master);
    json('SERIES_CONTINUITY_LOCK.json',result.lock);
    json('STYLE_LOCK.json',result.lock.styleLock);
    json(EP+'/LOCATION_MASTER.json',result.location);
    json(EP+'/QA_REPORT.json',result.qa);
    json(EP+'/metadata.json',{episode:1,canonicalStep6:'STEP6.json',characterMaster:'../CHARACTER_MASTER.json',revision:result.project.revision,status:'STRUCTURALLY_VALIDATED_IMPORT_TEST_PENDING',durationSeconds:36,locations:1,characters:3,imagesEmbedded:true});
    for (const id of IDS) files.push({name:SERIES+'/ASSETS/CHARACTERS/'+id+'-master.'+result.assets[id].extension,data:result.assets[id].bytes});
    files.push({name:SERIES+'/ASSETS/LOCATIONS/ep01-peach-tavern.'+result.assets.location.extension,data:result.assets.location.bytes});
    files.push({name:SERIES+'/'+EP+'/IMPORT_NOTE.txt',data:new TextEncoder().encode('Import STEP6.json only; it already contains STEP5 character images. STEP5.json is an optional inspection snapshot, not a second merge/import. Check thumbnails and references before generating. Original rendered clips are not reused. No changes to other series.\n')});
    return files;
  }
  function crc32(bytes) {
    let crc=0xffffffff;
    for(const b of bytes){crc^=b;for(let k=0;k<8;k++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}
    return (crc^0xffffffff)>>>0;
  }
  function makeZip(files) {
    const local=[],central=[];let offset=0,centralSize=0;
    for(const file of files){
      requireValue(!file.name.includes('..') && !file.name.startsWith('/'),'Unsafe ZIP path');
      const name=new TextEncoder().encode(file.name),data=file.data,crc=crc32(data);
      const h=new Uint8Array(30+name.length),v=new DataView(h.buffer);
      v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x0800,true);v.setUint16(12,33,true);v.setUint32(14,crc,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,name.length,true);h.set(name,30);
      local.push(h,data);
      const c=new Uint8Array(46+name.length),w=new DataView(c.buffer);
      w.setUint32(0,0x02014b50,true);w.setUint16(4,20,true);w.setUint16(6,20,true);w.setUint16(8,0x0800,true);w.setUint16(14,33,true);w.setUint32(16,crc,true);w.setUint32(20,data.length,true);w.setUint32(24,data.length,true);w.setUint16(28,name.length,true);w.setUint32(42,offset,true);c.set(name,46);central.push(c);centralSize+=c.length;offset+=h.length+data.length;
    }
    const e=new Uint8Array(22),v=new DataView(e.buffer);v.setUint32(0,0x06054b50,true);v.setUint16(8,files.length,true);v.setUint16(10,files.length,true);v.setUint32(12,centralSize,true);v.setUint32(16,offset,true);
    return [...local,...central,e];
  }
  const api={SERIES,EP,IDS,NAMES,NICKS,LOCATION,SCENES,assertSource,candidates,parseImage,sha256,build,validate,packageFiles,makeZip,crc32};
  if(typeof module!=='undefined' && module.exports)module.exports=api;else root.TKIEP01=api;
})(typeof globalThis!=='undefined'?globalThis:this);
