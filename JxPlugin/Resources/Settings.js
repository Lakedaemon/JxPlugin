$(document).ready(function(){	
	$('.edit_Model').editable(function(value, settings) {
		JxAnswerSettings.Model = value;
	       $('.edit_CardModel').remove();
	       $('.oltest').append("<b class='edit_CardModel'></b>");
	       	$('.edit_CardModel').editable(function(value, settings) { 
			JxAnswerSettings.CardModel = value;
			return value;
		},{ 
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
		$('.edit_Settings').html("gahhhhhhhhh");
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
});  
$(document).ready(function(){	
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
}); 
$(document).ready(function(){	

 $('.edit_Settings').editable(function(value, settings) { 
     console.log(this);
     console.log(value);
     console.log(settings);
     return(value);
  }, { 
     type    : 'textarea',
     submit  : 'OK',
 }); 
}); 
