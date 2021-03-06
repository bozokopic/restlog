import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from './common';
import * as vt from './vt';

import 'main.scss';


function main() {
    const root = document.body.appendChild(document.createElement('div'));
    r.init(root, common.state, vt.main);
    common.init();
}


window.addEventListener('load', main);
window.r = r;
window.u = u;
