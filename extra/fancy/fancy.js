/* Handles the hiding and showing */
$(document).ready(function(){
	
	$('li.sign-in').hide();
	$('li.sign-up').hide();
	
	$('a.sign-in').click(function(){
		$('li.sign-in').show('slow');
		$('li.sign-up').hide('slow');
	});
	
	$('a.sign-up').click(function(){
		$('li.sign-up').show('slow');
		$('li.sign-in').hide('slow');
	});	

});