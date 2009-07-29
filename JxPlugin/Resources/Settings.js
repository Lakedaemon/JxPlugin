	function Rename (){
		$('.Entry').html('<textarea name="Name" style="text-align:center" onBlur="Restore();" onChange="	JxTemplateOverride.Name = JxTemplateOverride.MakeUnique(document.forms.Translator.Name.value,0);Restore();">'+ JxTemplateOverride.Name +'</textarea>');	
		document.forms.Translator.Name.focus();
	};
	function Restore (){

		$('.Entry').html(JxTemplateOverride.GetForm());	
	};
$(document).ready(function(){
		document.forms.Translator.Source.value = JxTemplateOverride.Source;
		document.forms.Translator.Target.value = JxTemplateOverride.Target;
		$(".Entry").html(JxTemplateOverride.GetForm());
	
		
	// dropdown list checkboxes
	$("#s1").dropdownchecklist({ firstItemChecksAll: true,width:100});




});	

