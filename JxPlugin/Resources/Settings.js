$(document).ready(function(){
	$('.edit_Model').editable(function(value, settings) {
		JxAnswerSettings.Model = value;
		$('.edit_CardModel').html(JxAnswerSettings.CardModel);
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
	$('.edit_Settings').editable(function(value, settings) { 
		return(value);
	}, { 
		type    : 'textarea',
		submit  : 'OK',
	}); 

});	

