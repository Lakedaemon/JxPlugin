# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
Jx_Html_Menu = u""" 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html>
<head>
<title>JxPlugin Main Menu</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />


<!--                  jQuery & UI                          -->


<script type="text/javascript" src="js/jquery-1.3.2.min.js"></script>
<script type="text/javascript" src="js/jquery-ui-1.7.2.custom.min.js"></script>


<!--                         Theme                          -->

<link rel="Stylesheet" href="themes/sunny/jquery-ui.css" type="text/css" /> 
<!--<script type="text/javascript"  src="http://jqueryui.com/themeroller/themeswitchertool/"></script>--> 


<!--                         Tabs                          -->

<style type="text/css">
.ui-tabs .ui-tabs-hide {
     display: none;
}

#JxMenu ul li a{
        font-size:small;
        padding:5px;
}
</style>

<script type="text/javascript" src="js/ui.core.js"></script> 
<script type="text/javascript" src="js/ui.tabs.js"></script> 
<script type="text/javascript"> 
	$(function() {
		$("#JxMenu").tabs({
                        fx: { opacity: 'toggle' },
                        select: function(event, ui) {
                                if (ui.panel.id == "X"){
                                        JxWindow.Hide();
                                        return false;
                                };  
                                return true;
                         }
                  });
	});
</script> 


<!--                  Accordion                          -->

<script type="text/javascript" src="js/ui.accordion.js"></script> 
<script type="text/javascript">
	$(function() {
		$("#Settings").accordion({
			autoHeight: false
		});
                	$("#Tools").accordion({
			autoHeight: false
		});
	});
	</script>




<!--                  Buttons                          -->

<script src="ui.button/ui.classnameoptions.js"></script> 
<script src="ui.button/ui.button.js"></script> 
<link rel="stylesheet" type="text/css" href="ui.button/ui-button.css" /> 
<script src="ui.button/ui.buttonset.js"></script> 
<script type="text/javascript" >
        $(document).ready(function(){
               $('.ui-button').button({checkButtonset:true});
        });
</script> 


<!--                     Selects                          -->

<link rel="stylesheet" type="text/css" href="ui.dropdownchecklist.css" /> 
<script type="text/javascript" src="ui.dropdownchecklist.js"></script>

<link rel="Stylesheet" href="ui.selectmenu/ui.selectmenu.css" type="text/css" /> 
<script type="text/javascript" src="ui.selectmenu/ui.selectmenu.js"></script> 


<script type="text/javascript" src="Settings.js"></script>

<style type="text/css">

div#content {
	word-wrap: break-word;
}

textarea.Code { 
        border: #000000 1px solid; 
        color: #8187da; 
        background-color: #000000; 
        scrollbar-face-color: #000000; 
        scrollbar-highlight-color: #777777; 
        scrollbar-shadow-color: #777777; 
        scrollbar-3dlight-color: #000000; 
        scrollbar-arrow-color: #ff0000; 
        scrollbar-track-color: #333333; 
        scrollbar-darkshadow-color: #000000 
}
</style>


<script type="text/javascript">
$(document).ready(function(){
		$('select#Entry').selectmenu({width:200});
                  var temp = JxSettings.Get('Mode')
                  for(i=0; i<document.forms.FormMode.Mode.length; i++)
                        if(document.forms.FormMode.Mode.options[i].text == temp)
                           document.forms.FormMode.Mode.options.selectedIndex = i;
                  $('select#Mode').selectmenu({width:150});  
});
</script>

</head>
<body>
<div id="JxMenu">
<ul>
<li><a href="#JLPT">JLPT</a></li>
<li><a href="#Frequency">Frequency</a></li>
<li><a href="#Kanken">Kanken</a></li>
<li><a href="#Jouyou">Jouyou</a></li>
<li><a href="#Settings">Settings</a></li>
<li><a href="#Tools">Tools</a></li>
<li><a href="#X">X</a></li>
</ul>
<div id="JLPT">${JLPT}</div>
<div id="Frequency">${Frequency}</div>
<div id="Jouyou">${Jouyou}</div>
<div id="Kanken">${Kanken}</div>
<div id="Settings" style="padding:3px;">
	<h3><a href="#">About</a></h3>
	<div>
        The Japanese eXtended Plugin (V 1.14) aims to provide a complete set of usefull tools for the study of japanese.<br/><div style="text-align:center"><a href="http://github.com/Lakedaemon/JxPlugin/tree/master">Visit JxPlugin's home</a></div>
                <p>Written by Olivier Binda with patches from Robert Hebler.</p>
                <div><a style="display:block;" align="center" href='http://www.pledgie.com/campaigns/5354'><img alt='Click here to lend your support to: JxPlugin and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/5354.png?skin_name=chrome' border='0' /></a></div>
                <p>
                Thanks to all the people who have provided suggestions, bug reports and donations.</p>
	</div>
	<h3><a href="#">Answer Transductor</a></h3>
	<div>
                <center>
                <form name="FormMode">
                <select id="Mode" name="Mode" onChange="
                                var Index = document.forms.FormMode.Mode.options.selectedIndex;
                                JxSettings.Set('Mode',document.forms.FormMode.Mode.options[Index].text);
                        ">
                        <option name="Override">Override</option>    
                        <option name="Prepend">Prepend</option> 
                        <option name="Append">Append</option> 
                        <option name="Bypass">Bypass</option>
                </select>
                </form>
                </center>
                <br />
                <form name="Translator"> 
                <center><textarea  class="Code" name="Source" style="width: 70%%;height:50px;text-align:center;" onChange = "
                        JxTemplateOverride.Source = JxTemplateOverride.MakeUnique(document.forms.Translator.Source.value,1)
                "></textarea></center>
                <br/>
                <center class="Entry">&nbsp;</center>
                <br/>
                <center><textarea class="Code" name="Target" style="width: 90%%;height:100px;text-align:center;" onChange = "
                        JxTemplateOverride.Target = document.forms.Translator.Target.value
                " ></textarea></center>
                <br />
                <center><div class="ui-buttonset-tiny">
                        <a class="ui-button" href = "javascript:void(0)" onclick="
                                JxTemplateOverride.ResetTables();
                                JxTemplateOverride.Entry = 0;
                                $('.Entry').html(JxTemplateOverride.GetForm());
                                $('select#Entry').selectmenu({width:200});
                                document.forms.Translator.Target.value = JxTemplateOverride.Target;
                                document.forms.Translator.Source.value = JxTemplateOverride.Source;   
                         ">Reset</a>
                         <a class="ui-button" href = "javascript:void(0)" onClick="
                                $('.Entry').html(JxTemplateOverride.ReduceForm());
                                $('select#Entry').selectmenu({width:200});
                                $('.ui-button').button();
                                document.forms.Translator.Target.value=JxTemplateOverride.Target;
                                document.forms.Translator.Source.value=JxTemplateOverride.Source;"
                         >Delete</a>
                         <a class="ui-button" href = "javascript:void(0)" onClick="Rename()">Rename</a>
                         <a class="ui-button" href="py:JxBrowse()">Preview</a>
                         <a class="ui-button" href="py:JxHelp()">Help</a>
                </div>
                </center>
                </form>
	</div>
        
</div>
<div id="Tools">
        <h3><a href="#">Tag Redundant Entries</a></h3>
        <div>
        	       <center>
                       <select style="display:inline;" id="s1" multiple="multiple">%s</select>&nbsp;&nbsp;&nbsp;<a href=py:JxTagDuplicates(JxGetInfo())>Tag them !</a>
                </center>
                <ul>
                        <li>young ones get "JxDuplicate"</li>
                        <li>Oldest one gets "JxMasterDuplicate" and inherits all tags.</li>
                </ul>
        </div>
</div>
<div id="X">
</div>
</div> 
</body>
</html>
"""






################################################# Automatic mapping help ##########################################################





# todo : update
Jx_Html_HelpAutomaticMapping = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
  <head> 
    <meta http-equiv="content-type" content="text/html;charset=UTF-8" /> 
        <title>Documentation - JxPlugin - GitHub</title> 



 
    <meta name="description" content="Japanese Extended Plugin for the Spaced Repetition System ANKI" /> 
 
 
    
 
  </head> <body><style>
html,body{height:100%;}
body{background-color:white;font:13.34px helvetica,arial,clean,sans-serif;*font-size:small;text-align:center;}
table{font-size:inherit;font:100%;}
select,input[type=text],input[type=password],input[type=image],textarea{font:99% helvetica,arial,sans-serif;}
select,option{padding:0 .25em;}
input.text{padding:1px 0;}
optgroup{margin-top:.5em;}
pre,code{font:115% Monaco,"Courier New",monospace;*font-size:100%;}
body *{line-height:1.4em;}
img{border:0;}
a{color:#4183c4;text-decoration:none;}
a.action{color:#d00;text-decoration:underline;}
a.action span{text-decoration:none;}
a:hover{text-decoration:underline;}
.clear{clear:both;}
.sparkline{display:none;}
.right{float:right;}
.left{float:left;}
.hidden{display:none;}
img.help{vertical-align:middle;}
.notification{background:#FFFBE2 none repeat scroll 0;border:1px solid #FFE222;padding:1em;margin:1em 0;font-weight:bold;}
.warning{background:#fffccc;font-weight:bold;padding:.5em;margin-bottom:.8em;}
.error_box{background:#FFEBE8 none repeat scroll 0;border:1px solid #DD3C10;padding:1em;font-weight:bold;}
abbr{border-bottom:none;}
.flash{color:green;}
body{text-align:center;}  

</style>
<div >
        <h1><span class="caps">AUTOMATIC MAPPING</span></h1>
<p>These settings are usefull if you want to customize the display of the Answer cards when reviewing in Anki.</p>
<table align="center" style="border: 1px solid black;">
	<tbody><tr>
		<td colspan="3"><center><textarea style="border: 1px solid black; padding: 2px 40px; width: 150px; height: 30px;">%(Reading)s</textarea> &nbsp; <b>(1)</b></center></td>

	</tr>
	<tr>
		<td colspan="3"></td>
	</tr>
	<tr>
		<td style="text-align: center;"><b>(2)</b>&nbsp;<a>Delete</a></td>
		<td style="text-align: center;"><span style="border: 1px solid black; padding: 2px 40px;">Word recall </span><span style="border: 1px solid black; padding: 2px 5px;">V</span>&nbsp;<b>(3)</b></td>

		<td style="text-align: center;"><a>Rename </a>&nbsp;<b>(4)</b></td>
	</tr>
	<tr>
		<td colspan="3"></td>
	</tr>
	<tr>
		<td colspan="3"><center><textarea style="border: 1px solid black; padding: 2px 40px; width: 260px; height: 80px;">${Css}&lt;div style="float:left"&gt;&lt;div&gt;${T2JLPT}&lt;/div&gt;&lt;div&gt;${T2Freq}&lt;/div&gt;&lt;/div&gt;&lt;div&gt;&lt;center&gt;${Expression}&lt;br /&gt;${Reading}&lt;/center&gt;&lt;/div&gt;</textarea>&nbsp;<b>(5)</b></center></td>

	</tr>
	<tr>
		<td colspan="3"><center><b>(6)</b>&nbsp;<a>Preview</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a>Help</a>&nbsp;<b>(7)</b></center></td>
	</tr>
</tbody></table>
<h2>How to enhance the &quot;recognition&quot; template for Words</h2>
<p>You first select &quot;Word recognition&quot; in the select menu <b>(3)</b> to get</p>

<table align="center" style="border: 1px solid black;">
	<tbody><tr>
		<td colspan="3"><center><textarea style="border: 1px solid black; padding: 2px 40px; width: 170px; height: 35px;">%(Reading)s&lt;br&gt;%(Meaning)</textarea></center></td>
	</tr>
	<tr>
		<td colspan="3"></td>
	</tr>
	<tr>
		<td style="text-align: center;"><a>Delete</a></td>

		<td style="text-align: center;"><span style="border: 1px solid black; padding: 2px 40px;">Word recognition</span><span style="border: 1px solid black; padding: 2px 5px;">V</span>&nbsp;<b>(3)</b></td>
		<td style="text-align: center;"><a>Rename </a></td>
	</tr>
	<tr>
		<td colspan="3"></td>
	</tr>
	<tr>

		<td colspan="3"><center><textarea style="border: 1px solid black; padding: 2px 40px; width: 260px; height: 80px;">${Css} &lt;b&gt;(4)&lt;/b&gt;&lt;div style="float:left;"&gt;&lt;div&gt;${T2JLPT}&lt;/div&gt;&lt;div&gt;${T2Freq}&lt;/div&gt;&lt;/div&gt;&lt;div&gt;&lt;center&gt;${Reading}&lt;br&gt;${Meaning}&lt;/center&gt;&lt;/div&gt;</textarea></center></td>
	</tr>
	<tr>
		<td colspan="3"><center><a>Preview</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a>Help</a></center></td>
	</tr>
</tbody></table>
<p>Then, you modify the field <b>(5)</b> to your liking, using <span class="caps">HTML</span> and Css markup. The JxPlugin ads support for some special symbols related to the study of japanese that you can use too like $(CSS), $([Field Name]), $(WJLPT), $(TJLPT), …</p>

<table align="center" style="border: 1px solid black;">
	<tbody><tr>
		<td colspan="3"><center><textarea style="border: 1px solid black; padding: 2px 40px; width: 170px; height: 35px;">%(Reading)s&lt;br&gt;%(Meaning)</textarea></center></td>
	</tr>
	<tr>
		<td colspan="3"></td>
	</tr>
	<tr>
		<td style="text-align: center;"><a>Delete</a></td>

		<td style="text-align: center;"><span style="border: 1px solid black; padding: 2px 40px;">Word recognition</span><span style="border: 1px solid black; padding: 2px 5px;">V</span></td>
		<td style="text-align: center;"><a>Rename </a></td>
	</tr>
	<tr>
		<td colspan="3"></td>
	</tr>
	<tr>

		<td colspan="3"><center><textarea style="border: 1px solid black; padding: 2px 40px; width: 260px; height: 80px;">&lt;center&gt;My markup code for $(Expression)&lt;/center&gt;JLPT Level is : $(WJLPT)</textarea>&nbsp;<b>(5)</b></center></td>
	</tr>
	<tr>
		<td colspan="3"><center><a>Preview</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a>Help</a></center></td>
	</tr>
</tbody></table>
      </div><p></p></body></html>
"""
