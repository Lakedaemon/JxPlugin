$(document).ready(function(){
	$('.edit_Mode').editable(function(value, settings) {
		JxAnswerSettings.Mode = value;
		return value;
	}, { 
		onblur : 'submit',
		indicator : '<img src="img/indicator.gif">',
		data   : {'Append':'Apend','Prepend':'Prepend','Overide':'Overide','selected':'Append'},
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
	$('.edit_DisplayString').editable(function(value, settings) { 
		return(value);
	}, { 
		type    : 'textarea',
		placeholder : JxAnswerSettings.DisplayString,
		width : 250,
		height : 100,
		onblur : 'submit'
	}); 

});	

