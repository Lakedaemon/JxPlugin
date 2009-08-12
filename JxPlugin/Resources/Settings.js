	function Rename (){
                if (JxTemplateOverride.Name != "New Entry") {
		$('.Entry').html('<textarea name="Name" style="text-align:center" onBlur="Restore();" onChange="	JxTemplateOverride.Name = JxTemplateOverride.MakeUnique(document.forms.Translator.Name.value,0);Restore();">'+ JxTemplateOverride.Name +'</textarea>');	
		document.forms.Translator.Name.focus();
                };
	};
	function Restore (){

		$('.Entry').html(JxTemplateOverride.GetForm());
                $('select#Entry').selectmenu({width:200});
	};
$(document).ready(function(){
		document.forms.Translator.Source.value = JxTemplateOverride.Source;
		document.forms.Translator.Target.value = JxTemplateOverride.Target;
		$(".Entry").html(JxTemplateOverride.GetForm());
		$('select#Entry').selectmenu({width:200});
		




});	

