*----------------------------------------------------------------------------------------------------
*----------------------------------气候冲击与企业违约风险——基于物理风险的视角------------------------------------
*-----------------------------------------------------------------------------------------------------




	**======描述性统计【见附录表8】======**
	
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\基准回归检验\基准回归.dta"   
*注：请根据文件的实际位置进行调整，下同

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"
sum NP PhyClimt $cv



	**======变量有效性检验======**
	
	
	//灾害损失和减值损失视角检验指标有效性【见附录表2和表4】
	
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\指标有效性检验\灾害损失和减值损失检验指标有效性.dta"

*附表2
pwcorr MNP EcoLoss StEcoLoss Pop StPop, sig star(0.01)


*附表4
pwcorr MNP assloss, sig star(0.05)
pwcorr MNP fixassloss, sig star(0.01)


	//年报文本特征视角检验指标有效性【见附录表5】
	
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\指标有效性检验\年报文本特征视角检验指标有效性.dta"

*附表5
pwcorr PhyClimt neg, sig star(0.01)

pwcorr absPhyClimt simity, sig star(0.01)

pwcorr PhyClimt media , sig star(0.1)


	//企业特征视角检验指标有效性【见附录表6】
	
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\指标有效性检验\企业特征视角检验指标有效性.dta"

*附表6
global cvyxx "assets fixedassets geo pod ecoloss indds gi age"

reg PhyClimt $cvyxx, r

reg f.PhyClimt $cvyxx, r


	//企业信息披露视角检验指标有效性【见附录表7】
	
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\指标有效性检验\企业信息披露视角检验指标有效性.dta"

pwcorr PhyClimt invest , sig star(0.05)

pwcorr PhyClimt announce , sig star(0.1)

pwcorr PhyClimt esg1 esg2 , sig star(0.01)


pwcorr PhyClimt survey , sig star(0.01)

pwcorr PhyClimt sunyi, sig star(0.05)

pwcorr PhyClimt loss , sig star(0.01)

pwcorr PhyClimt amtsub subsidy, sig star(0.01)

pwcorr PhyClimt ri, sig star(0.01)



	**======主回归结果【见正文表1】======**
	
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\基准回归检验\基准回归.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

global cv1 " Lnassets Roa Lev Fixed_assets Cash"

global cv2 " Lndsh Inddszb Lnggxc Nage Pe"

xtreg NP PhyClimt  i.year,fe r

xtreg NP PhyClimt $cv1  i.year,fe r

xtreg NP PhyClimt $cv2 i.year,fe r

xtreg NP PhyClimt $cv i.year,fe r



	**======替换解释变量度量方法【见附录表9】======**
	
xtreg NP PhyClimt1 $cv i.year,fe r

xtreg NP PhyClimt2 $cv i.year,fe r

xtreg NP PhyClimt3 $cv i.year,fe r

xtreg NP PhyClimt4 $cv i.year,fe r

xtreg NP PhyClimt5 $cv i.year,fe r



	**======内生性检验======**

	
	 //变量滞后一期【见附录表10列1】
	 
xtreg f.NP PhyClimt $cv i.year,fe r


	 //工具变量【见附录表10列2、3】
	 
xtivreg NP (PhyClimt=IV ) $cv i.year,fe first vce(cluster code)


	 //两阶段残差介入【见附录表10列4】
	 
xtreg NP e $cv i.year,fe r


	 //剔除适应性行为影响【见附录表10列5】
	 
xtreg NP e1 $cv i.year,fe r



	**======稳健性检验======**
	
	
	 //替换被解释变量检验方法【见附录表11列1、2】
	 
xtreg NP1 PhyClimt $cv i.year, fe r

xtreg NP2 PhyClimt $cv i.year, fe r


	 //考虑气候物理冲击的时滞效应【见附录表11列3】
	 
xtreg NP mPhyClimt $cv i.year, fe r


    //扩充控制变量范围【见附录表11列4】
	
xtreg NP PhyClimt $cv loss1 loss2 loss3 loss4 i.year, fe r


    //控制宏观系统性因素【见附录表11列5】
	
xtreg NP PhyClimt $cv  i.year  i.year#i.p i.year#i.ind, fe r


    //更换模型设定形式【见附录表11列6】
	
xttobit fx_lnkmv_w fx_cip fx_lnassets fx_roa fx_lev fx_fa fx_cash fx_lndsh fx_inddszb fx_lnggxc fx_nage  fx_pe i.year


	
	**======机制检验======**

	
	 //实体效应检验【见正文表2】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\机制检验\机制检验实体效应DA.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg DA PhyClimt $cv i.year,fe r

xtreg NP DA $cv i.year,fe r	 

use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\机制检验\机制检验实体效应Netprofit.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg Net_profit PhyClimt $cv i.year,fe r

xtreg NP Net_profit $cv i.year,fe r

use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\机制检验\机制检验实体效应Profit.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg Profit PhyClimt $cv i.year,fe r

xtreg NP Profit $cv i.year,fe r


	 //资本市场效应检验【见正文表3】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\机制检验\机制检验资本市场效应Q.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg Q PhyClimt $cv i.year,fe r

xtreg NP Q $cv i.year,fe r


	 //资本市场效应的三阶段检验【见正文表4】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\机制检验\机制检验资本市场效应三阶段检验.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg DA PhyClimt $cv i.year,fe r

xtreg Q DAbar $cv i.year,fe r

xtreg NP Qbar1 $cv i.year,fe r

xtreg Net_profit PhyClimt $cv i.year,fe r

xtreg Q Net_profitbar $cv i.year,fe r

xtreg NP Qbar2 $cv i.year,fe r

xtreg Profit PhyClimt $cv i.year,fe r

xtreg Q Profitbar $cv i.year,fe r

xtreg NP Qbar3 $cv i.year,fe r



	**======进一步分析======**

	
	 //调节效应检验【见正文表5】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\进一步分析\协同效应分析\insurance.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg NP PhyClimt_Ins PhyClimt insurance $cv i.year, fe r

use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\进一步分析\协同效应分析\HHI.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg NP PhyClimt_HHI PhyClimt HHI $cv i.year, fe r

use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\进一步分析\协同效应分析\KV.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg NP PhyClimt_KV PhyClimt KV $cv i.year, fe r


	 //关联性分析【见正文表6】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\进一步分析\关联性分析\关联性分析.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg NP PhyClimt $cv i.year if bitr ==1,fe r

xtreg NP PhyClimt $cv i.year if bitr ==0,fe r

xtreg NP PhyClimt $cv i.year if bigredev ==1,fe r

xtreg NP PhyClimt $cv i.year if bigredev ==0,fe r


	 //物理风险对企业生产经营的进一步影响【见正文表7、8】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\进一步分析\物理风险对企业生产经营的进一步影响\物理风险对企业生产经营的进一步影响.dta"

global cv " Lnassets Roa Lev Fixed_assets Cash Lndsh Inddszb Lnggxc Nage Pe"

xtreg DA PhyClimt $cv i.year,fe r

xtreg NP DAbar $cv i.year,fe r

xtreg f.SA NPbar1 $cv i.year,fe r

xtreg f.risktaking NPbar1 $cv i.year,fe r

xtreg Net_profit  PhyClimt $cv i.year,fe r

xtreg NP Net_profitbar $cv i.year,fe r

xtreg f.SA NPbar2 $cv i.year,fe r

xtreg f.risktaking NPbar2 $cv i.year,fe r

xtreg Profit  PhyClimt $cv i.year,fe r

xtreg NP Profitbar $cv i.year,fe r

xtreg f.SA NPbar3 $cv i.year,fe r

xtreg f.risktaking NPbar3 $cv i.year,fe r


	 //企业违约风险向金融体系传导效应检验【见正文表9】
	 
use "C:\Users\王策建议\Desktop\企业物理风险研究复现材料\进一步分析\企业违约风险向金融体系传导效应检验\企业违约风险向金融体系传导效应检验.dta"

global cv "lnassets roa cti dtl dd pta"

xtreg lnnp NPbar $cv i.year, fe r

xtreg lnnp NPBbar $cv i.year, fe r

xtreg lnnp NPRIbar $cv i.year, fe r




















