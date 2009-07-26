$(document).ready(function(){
	// dropdown list checkboxes
	$("#s1").dropdownchecklist({ firstItemChecksAll: true,width:100});

	// Linked selects
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
	// Source-> Target
	$('.edit_CardTemplate').editable(function(value, settings) {
		JxTemplateOverride.Entry = value;
		$('.edit_SourceTemplate').html(JxTemplateOverride.Source);
		$('.edit_TargetTemplate').html(JxTemplateOverride.Target);
		return value;
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : JxTemplateOverride.GetEntries,
//		placeholder : 'Append',
		type   : "select",
		style  : "inherit",
		tooltip   : "Click to edit model !",
		submitdata : function() {
			return {id : 2};
		}
	});
	$('.edit_NameTemplate').html(JxTemplateOverride.Entry);
	$('.edit_NameTemplate').editable(function(value, settings) { 
		return(value);
	}, { 
		type    : 'textarea',
		onblur : 'submit'
	}); 
	$('.edit_SourceTemplate').html(JxTemplateOverride.Source);
	$('.edit_SourceTemplate').editable(function(value, settings) {
		JxTemplateOverride.Source = value;
		return(value);
	}, { 
		type    : 'textarea',
		width : 150,
		height : 100,
		onblur : 'submit'
	}); 
	$('.edit_TargetTemplate').html(JxTemplateOverride.Target);
	$('.edit_TargetTemplate').editable(function(value, settings) {
		JxTemplateOverride.Target = value;
		return(value);
	}, { 
		type    : 'textarea',
		width : 150,
		height : 100,
		onblur : 'submit'
	}); 
});	

