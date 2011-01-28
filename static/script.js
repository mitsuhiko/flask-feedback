function makeFeedbackBox(feedback) {
  var charsLeft, feedbackInput, errorLog = null;

  function showFormError(error) {
    if (errorLog === null)
      errorLog = $('<p class=error></p>').insertAfter('.feedback p.version');
    errorLog.hide().slideDown();
    errorLog.text(error);
  }

  function updateCharsLeft() {
    var delta = 140 - feedbackInput.val().length;
    charsLeft.text('' + delta);
    charsLeft.toggleClass('chars-over-limit', delta < 0);
    if (!charsLeft.is(':visible'))
      charsLeft.fadeIn('slow');
  }

  function calculateResponse() {
    var challenge = +$('input[name="challenge"]', feedback).val();
    return parseInt((challenge / 2) + (challenge / 3) - (challenge / 4));
  }
  
  function justWantedToSayThatIm(kind) {
    return function() {
      updateCharsLeft();
      var step2 = $('#step-2', feedback);
      $('input[name="kind"]').val(kind);
      $('.kind-selector', feedback).removeClass('active-kind');
      $(this).parent().addClass('active-kind');
      if (!step2.is(':visible')) {
        $('textarea', step2).val('');
        step2.slideDown('fast', function() {
          $('textarea', step2).focus();
        });
      }
      return false;
    };
  }

  feedback.bind('submit', function() {
    if (this.feedback.value.length > 140) {
      showFormError('Your message is too long :-(');
      return false;
    }
    if (this.version.value.length > 0 &&
        !this.version.value.match(/^((\d{1,5}\.\d{1,5}(\.\d{1,3})?)|(dev))$/)) {
      showFormError('Malformed version.  Use Major.Minor or dev');
      return false;
    }
  });

  $($('li', feedback).hide()[0]).show();
  $('a.happy', feedback).click(justWantedToSayThatIm('happy'));
  $('a.unhappy', feedback).click(justWantedToSayThatIm('unhappy'));
  feedbackInput = $('p.text textarea', feedback)
    .keyup(function() {
      updateCharsLeft();
      var nextStep = $('#step-3', feedback);
      if (this.value.length >= 5)
        nextStep.slideDown('fast');
      else
        nextStep.slideUp('fast');
    });
  charsLeft = $('<span class=chars-left></span>')
    .insertBefore(feedbackInput)
    .hide();
  feedback.animate({height: 'show', opacity: 'show'});

  /* get away stupid spam */
  $('<input type=hidden name=response>')
    .val(calculateResponse())
    .insertAfter('input[name="challenge"]', feedback);
}

$(function() {
  var feedback = $('.feedback');
  if (feedback.length)
    makeFeedbackBox(feedback);
  $('.javascript-required').hide();
});
