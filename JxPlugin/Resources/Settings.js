function Escape(value){
	var String = value;
return String.replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
function UnEscape(value){
	var String = value;
return String.replace(/&lt;/g,"<").replace(/&gt;/g,">");
}
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
		$('.edit_NameTemplate').html(Escape(JxTemplateOverride.Name));
		$('.edit_SourceTemplate').html(Escape(JxTemplateOverride.Source));
		$('.edit_TargetTemplate').html(Escape(JxTemplateOverride.Target));
		return Escape(JxTemplateOverride.Name);
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : JxTemplateOverride.GetEntries,
		placeholder : Escape(JxTemplateOverride.Name),
		type   : "select",
		style  : "inherit",
		tooltip   : "Click to choose a card template mapping !",
		submitdata : function() {
			return {id : 2};
		}
	});
	$('.edit_NameTemplate').editable(function(value, settings) { 
		JxTemplateOverride.Name = value;
		$('.edit_CardTemplate').html(Escape(JxTemplateOverride.Name));
		return Escape(JxTemplateOverride.Name);
	}, { 
		type    : 'textarea',
		data : function(value,settings) {return JxTemplateOverride.Name;},
		placeholder : Escape(JxTemplateOverride.Name),
		onblur : 'submit'
	}); 
	$('.edit_SourceTemplate').editable(function(value, settings) {
		uniquevalue = JxTemplateOverride.MakeSourceUnique(value)
		JxTemplateOverride.Source = uniquevalue;
		return Escape(uniquevalue);
	}, { 
		type    : 'textarea',
		data : function(value,settings) {return JxTemplateOverride.Source;},
		placeholder : Escape(JxTemplateOverride.Source),
		width : 150,
		height : 100,
		onblur : 'submit'
	}); 
	$('.edit_TargetTemplate').editable(function(value, settings) {
		JxTemplateOverride.Target = value;
		return Escape(value);
	}, { 
		type    : 'textarea',
		data : function(value,settings) {return JxTemplateOverride.Target;},
		placeholder : Escape(JxTemplateOverride.Target),
		width : 150,
		height : 100,
		onblur : 'submit'
	});
});	

