from bokeh.util.compiler import JavaScript
from bokeh.models import CustomJS
from bokeh.model import Model
from bokeh.core.properties import Int, String


class LoadingProps(Model):
    __implementation__ = JavaScript("""
        import * as p from "core/properties"
        import {Model} from "model"
        export class LoadingProps extends Model {}

        LoadingProps.define({
            num_loaded:   [ p.Int ],
            num_to_load:   [ p.Int ],
            file_loading:  [ p.String ],
            loading_error:  [ p.String ],
            workflow_loading:  [ p.String ],
        })
        """
    )

    num_loaded = Int(0)
    num_to_load = Int(0)
    file_loading = String()
    loading_error = String()
    workflow_loading = String()


def get_loading_modal_update_callback():
    callback = CustomJS(code="""
        var modalTxt = document.getElementById('loadModalText');

        modalTxt.textContent = 'Loading ' + cb_obj.file_loading + ' (' + cb_obj.num_loaded + '/' + cb_obj.num_to_load + ')...';
        console.log('cb_obj.num_loaded:' + cb_obj.num_loaded);
    """
    )

    return callback

def get_loading_modal_callback():
    callback = CustomJS(code="""
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];

        var modalTxt = document.getElementById('loadModalText');

        if ( cb_obj.num_to_load == 0 ) {
            modal.style.display = "none";
        } else {
            // When the user clicks on <span> (x), close the modal
            span.onclick = function() {
                modal.style.display = "none";
            }

            // When the user clicks anywhere outside of the modal, close it
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }

            modalTxt.textContent = 'Loading ' + cb_obj.file_loading + ' (0/' + cb_obj.num_to_load + ')...';
            modal.style.display = "block";
        }
    """
    )

    return callback

def get_loading_error_callback():
    callback = CustomJS(code="""
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];
        var modalTxt = document.getElementById('loadModalText');
        var err_msg = cb_obj.loading_error;

        if ( err_msg.length > 0 ) {
            // When the user clicks on <span> (x), close the modal
            span.onclick = function() {
                modal.style.display = "none";
            }

            // When the user clicks anywhere outside of the modal, close it
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }

            modalTxt.textContent = err_msg;
            modal.style.display = "block";
        }
    """
    )

    return callback

def get_loading_workflow_callback():
    callback = CustomJS(code="""
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];
        var modalTxt = document.getElementById('loadModalText');
        var wf_msg = cb_obj.workflow_loading;

        if ( wf_msg.length > 0 ) {
            // When the user clicks on <span> (x), close the modal
            span.onclick = function() {
                modal.style.display = "none";
            }

            // When the user clicks anywhere outside of the modal, close it
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }

            modalTxt.textContent = wf_msg;
            modal.style.display = "block";
        } else {
            modal.style.display = "none";
        }
    """
    )

    return callback