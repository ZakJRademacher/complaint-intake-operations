import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(process.env.RETAIL_ARTIFACT_ROOT ? path.join(process.env.RETAIL_ARTIFACT_ROOT,'package.json') : import.meta.url);
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const root=path.resolve(process.argv[2]);
const input=JSON.parse(await fs.readFile(path.join(root,'results/analysis.json'),'utf8'));
const m=input.metrics,r=input.reports;
const wb=Workbook.create();
const main=wb.worksheets.add('Operations review'),monthly=wb.worksheets.add('Monthly'),queue=wb.worksheets.add('Review queue');
const navy='#18283F',blue='#3067B0',muted='#65758A',green='#087F73';
for(const s of [main,monthly,queue]){
 s.showGridLines=false;
 s.getRange('A1:K110').format.font={name:'Arial',size:10,color:navy};
 s.getRange('A1:K110').format.rowHeight=24;
 s.getRange('A1:K110').format.columnWidth=17;
 s.freezePanes.freezeRows(5);
}
function title(s,text,subtitle){s.getRange('A2').values=[[text]];s.getRange('A2').format.font={size:18,bold:true};s.getRange('A3').values=[[subtitle]];s.getRange('A3').format.font={size:10,color:muted};}
function head(s,range){s.getRange(range).format={fill:navy,font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:40};}
title(main,'Complaint intake & response operations','903,983 historical records | Dec 2011–Nov 15, 2017 | Personal portfolio project');
main.getRange('A5:B5').values=[['Metric','Value']];
main.getRange('A6:B12').values=[['Complaint records',null],['Source timely: Yes',null],['Known response denominator',null],['Source timely rate',null],['Valid routing intervals',null],['Negative date intervals',null],['Routing > review days',null]];
const ce=19+r.channels.length;
main.getRange('B6:B12').formulas=[[`=SUM(B20:B${ce})`],[`=SUM(C20:C${ce})`],[`=SUM(C20:D${ce})`],['=IF(B8=0,"n.a.",B7/B8)'],[`=SUM(F20:F${ce})`],[`=SUM(G20:G${ce})`],[`=SUM(I20:I${ce})`]];
main.getRange('A14:B15').values=[['Review threshold (days)',m.review_days],['Flagged cases (all reasons)',m.review_queue_cases]];
main.getRange('B14:B15').format.font.color=blue;
main.getRange('A16').values=[['Threshold is a demo review rule; regenerate SQL to change it. No regulatory SLA implied.']];
main.getRange('A17').values=[['Routing = sent date minus received date. Source timely flag measures a different event.']];
main.getRange('A16:A17').format.font={size:9,color:muted};
main.getRange('A19:K19').values=[['Channel','Cases','Timely Yes','Timely No','Unknown flag','Valid intervals','Negative dates','Invalid dates','Routing > days','Mean days','P90 days']];
main.getRange(`A20:K${ce}`).values=r.channels.map(x=>[x.channel,x.cases,x.timely_yes,x.timely_no,x.timely_unknown,x.valid_intervals,x.negative_intervals,x.invalid_dates,x.over_review_days,x.valid_intervals?x.total_intake_days/x.valid_intervals:null,x.p90_days]);
main.getRange(`B20:K${ce}`).format.font.color=blue;
main.getRange('A5:A15').format.columnWidth=31;main.getRange('B6:B15').setNumberFormat('#,##0');main.getRange('B9').setNumberFormat('0.0%');
main.getRange(`B20:I${ce}`).setNumberFormat('#,##0');main.getRange(`J20:K${ce}`).setNumberFormat('0.0');
main.getRange('A28').values=[['Interpretation and handoff']];main.getRange('A28').format.font={bold:true,size:12};
main.getRange('A29').values=[['Negative intervals stay in case counts and leave all duration denominators.']];
main.getRange('A30').values=[['Review queue shows 100 longest valid routing delays; the full flagged CSV is generated locally.']];
main.getRange('A31').values=[['November 2017 is partial through Nov 15. This historical snapshot is not a live backlog.']];
main.getRange('A33').values=[['Source: Kaggle sebastienverpile/consumercomplaintsdata (CC0), originally CFPB.']];
main.getRange('A34').values=[['Public complaints are not a representative sample. No company quality comparison is made.']];
main.getRange('A33:A34').format.font={size:9,color:muted};
title(monthly,'Monthly intake review','Blue imports; dark formulas. Final month is partial. Timely rate excludes unknown flags.');
monthly.getRange('A5:I5').values=[['Received month','Cases','Timely Yes','Timely No','Unknown flag','Timely rate','Valid intervals','Routing > days','Routing review rate']];
const me=5+r.monthly.length;
monthly.getRange(`A6:I${me}`).values=r.monthly.map(x=>[x.month+(x.month===m.last_received.slice(0,7)?' partial':''),x.cases,x.timely_yes,x.timely_no,x.timely_unknown,null,x.valid_intervals,x.over_review_days,null]);
for(let row=6;row<=me;row++){
 monthly.getRange(`F${row}`).formulas=[[`=IF(C${row}+D${row}=0,"n.a.",C${row}/(C${row}+D${row}))`]];
 monthly.getRange(`I${row}`).formulas=[[`=IF(G${row}=0,"n.a.",H${row}/G${row})`]];
}
for(const c of ['B','C','D','E','G','H'])monthly.getRange(`${c}6:${c}${me}`).format.font.color=blue;
monthly.getRange(`B6:E${me}`).setNumberFormat('#,##0');monthly.getRange(`G6:H${me}`).setNumberFormat('#,##0');
monthly.getRange(`F6:F${me}`).setNumberFormat('0.0%');monthly.getRange(`I6:I${me}`).setNumberFormat('0.0%');monthly.getRange(`A${me}:I${me}`).format.fill='#FFF2DF';
title(queue,'Review queue · 100 examples','Longest valid routing delays, not a representative sample. Only blue Owner / Review status / Notes cells are editable.');
queue.getRange('A5:J5').values=[['Complaint ID','Product','Received','Sent to company','Routing days','Review reason','Owner','Review status','Notes','Next action']];
const qe=5+r.review_queue.length;
queue.getRange(`A6:J${qe}`).values=r.review_queue.map(x=>[x.complaint_id,x.product,x.received,x.sent,x.intake_days,x.review_reason,x.owner,x.review_status,x.notes,null]);
queue.getRange(`A6:A${qe}`).setNumberFormat('@');
for(let row=6;row<=qe;row++) queue.getRange(`J${row}`).formulas=[[`=IF(H${row}="Resolved",IF(AND(G${row}<>"",I${row}<>""),"Complete","Add owner and note"),IF(G${row}="","Assign owner","Review evidence"))`]];
queue.getRange(`G6:I${qe}`).format={fill:'#EDF6FF',font:{color:blue},wrapText:true};
queue.getRange(`H6:H${qe}`).dataValidation={rule:{type:'list',values:['Not started','In progress','Resolved']}};
queue.getRange('B5:B105').format.columnWidth=24;queue.getRange('F5:F105').format.columnWidth=29;queue.getRange('I5:I105').format.columnWidth=32;queue.getRange('J5:J105').format.columnWidth=24;
queue.getRange(`A6:J${qe}`).format.rowHeight=42;queue.getRange(`A6:J${qe}`).format.wrapText=true;
monthly.getRange('K5:L5').values=[['Month · chart inputs','Cases']];
for(let i=0;i<12;i++){
 const source=me-11+i, row=6+i;
 monthly.getRange(`K${row}:L${row}`).formulas=[[`=A${source}`,`=B${source}`]];
}
const chart=main.charts.add('column',monthly.getRange('K5:L17'));
chart.title='Last 12 observed months · final month partial';chart.hasLegend=false;chart.titleTextStyle.fontSize=11;chart.xAxis={axisType:'textAxis',textStyle:{fontSize:8}};chart.yAxis={numberFormatCode:'#,##0',textStyle:{fontSize:9}};chart.setPosition('D5','L15');
main.tables.add(`A19:K${ce}`,true,'ChannelReview');monthly.tables.add(`A5:I${me}`,true,'MonthlyReview');queue.tables.add(`A5:J${qe}`,true,'CaseReview');
head(main,'A5:B5');head(main,'A19:K19');head(monthly,'A5:I5');head(queue,'A5:J5');
queue.getRange(`G6:I${qe}`).format.fill='#EDF6FF';queue.getRange(`G6:I${qe}`).format.font.color=blue;
wb.recalculate();
if(main.getRange('B6').values[0][0]!==m.cases)throw Error('Case count mismatch');
if(Math.abs(main.getRange('B9').values[0][0]-m.timely_rate)>1e-10)throw Error('Rate mismatch');
const old=main.getRange('B20').values[0][0];main.getRange('B20').values=[[old+1]];wb.recalculate();
if(main.getRange('B6').values[0][0]!==m.cases+1)throw Error('Count propagation failed');main.getRange('B20').values=[[old]];
queue.getRange('H6').values=[['Resolved']];wb.recalculate();if(queue.getRange('J6').values[0][0]!=='Add owner and note')throw Error('Resolution guard failed');
queue.getRange('G6').values=[['Test reviewer']];queue.getRange('I6').values=[['Test evidence']];wb.recalculate();if(queue.getRange('J6').values[0][0]!=='Complete')throw Error('Resolution completion failed');
queue.getRange('G6:I6').values=[[r.review_queue[0].owner,r.review_queue[0].review_status,r.review_queue[0].notes]];wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final formula error scan'});
await fs.writeFile(path.join(root,'docs/workbook-verification.json'),JSON.stringify({caseCountMatches:true,responseRateMatches:true,inputChangePropagates:true,resolutionGuardWorks:true,inputsRestored:true,errorScan:errors.ndjson,nativeExcelTested:false},null,2));
for(const [s,range,file] of [[main,'A1:L34','excel-operations-preview.png'],[monthly,'A1:I19','excel-monthly-preview.png'],[queue,'A1:J12','excel-queue-preview.png']]){
 const blob=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});await fs.writeFile(path.join(root,'deliverables',file),new Uint8Array(await blob.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(root,'deliverables/complaint-operations-review.xlsx'));
console.log(JSON.stringify({caseCount:m.cases,rate:m.timely_rate,errorScan:errors.ndjson}));
