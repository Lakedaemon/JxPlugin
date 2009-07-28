	function Rename (){
		$('.Entry').html('<textarea name="Name" style="text-align:center" onChange="Restore()">'+ JxTemplateOverride.Name +'</textarea>');	
	};
	function Restore (){
		JxTemplateOverride.Name = JxTemplateOverride.MakeUnique(document.forms.Translator.Name.value,0);
		$('.Entry').html(JxTemplateOverride.GetForm());	
	};
$(document).ready(function(){
		document.forms.Translator.Source.value = JxTemplateOverride.Source;
		document.forms.Translator.Target.value = JxTemplateOverride.Target;
		$(".Entry").html(JxTemplateOverride.GetForm());
	
		
	// dropdown list checkboxes
	$("#s1").dropdownchecklist({ firstItemChecksAll: true,width:100});

	// Linked selects
	$('.edit_Model').editable(function(value, settings) {
		JxAnswerSettings.Model = value;
		$('.edit_CardModel').html(JxAnswerSettings.CardModel);
		$('.edit_DisplayString').html(JxAnswerSettings.DisplayString);
		return value;
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : JxAnswerSettings.GetModels,
		placeholder : JxAnswerSettings.Model,
		type   : "select",
		style  : "inherit",
		tooltip   : "Click to edit model !",
		submitdata : function() {
			return {id : 2};
		}
	});
	$('.edit_CardModel').editable(function(value, settings) { 
	       JxAnswerSettings.CardModel = value;
	       	$('.edit_DisplayString').html(JxAnswerSettings.DisplayString);
	       return(value);
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : JxAnswerSettings.GetCardModels,
		placeholder : JxAnswerSettings.CardModel,
		type   : "select",
		style  : "inherit",
		submitdata : function() {
			return {id : 2};
		}
	});
	$('.edit_DisplayString').html(JxAnswerSettings.DisplayString);
	$('.edit_DisplayString').editable(function(value, settings) { 
		return(value);
	}, { 
		type    : 'textarea',
		width : 250,
		height : 100,
		onblur : 'submit'
	}); 
	
	
	
	
		$('.edit_Mode').editable(function(value, settings) {
		//JxAnswerSettings.Mode = value;
		return value;
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : {'Append':'Append','Prepend':'Prepend','Override':'Override','selected':'Append'},
		placeholder : 'Append',
		type   : "select",
		style  : "inherit",
		tooltip   : "Click to edit model !",
		submitdata : function() {
			return {id : 2};
		}
	});
	$('.edit_ChooseKey').editable(function(value, settings) {
		//JxAnswerSettings.Mode = value;
		return value;
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : {'Append':'Append','Prepend':'Prepend','Override':'Override','selected':'Append'},
		placeholder : 'Append',
		type   : "select",
		style  : "inherit",
		tooltip   : "Click to edit model !",
		submitdata : function() {
			return {id : 2};
		}
	});
	


});	

