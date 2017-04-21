// Ajax form with page animations

$(function() {
    var frm = $('#predict_form');

    frm.submit(function(e){
        e.preventDefault();
        var loaderContainer = $('.loader-container');
        var preloader= $('#preloader');
        var loader= $('#loader');
        var results = $('#results');
        var fieldset = $('fieldset', this);
        var formData = {
            'text': $('textarea[name=text]').val(),
        };
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: formData,
            success: function (data) {
                loaderContainer.addClass('hidden');
                results.removeClass('hidden');
                fieldset.attr('disabled', false);

                $("#predict_errors").addClass('hidden');
                $("#predict_results").html(data['predicted_forum']);
                console.log(data);
            },
            error: function(data) {
                $("#predict_errors").removeClass('hidden');
                $("#predict_errors").html("<p>Something went wrong!</p>");
                loader.addClass('hidden');
                preloader.removeClass('hidden');
            }
        });
        fieldset.attr('disabled', true);
        preloader.addClass('hidden');
        results.addClass('hidden');
        loader.removeClass('hidden');
        loaderContainer.removeClass('hidden');
        return false;
    });
});
