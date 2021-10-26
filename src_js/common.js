import r from '@hat-open/renderer';


const localTimezoneOffset = (new Date()).getTimezoneOffset() * 60;


export const state = {
    entries: []
};


export function init() {
    fetch('/entries').then(response =>
        response.json()
    ).then(data =>
        r.set('entries', data['entries'])
    );
}


export function timestampToString(timestamp) {
    const date = new Date((timestamp - localTimezoneOffset) * 1000);
    return date.toISOString().replace('T', ' ').replace('Z', '');
}
