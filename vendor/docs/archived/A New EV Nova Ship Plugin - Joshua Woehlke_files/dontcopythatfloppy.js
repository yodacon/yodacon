import { globals } from "./modules/globals.mjs";
import * as helpers from "./modules/helpers.mjs";

///////////////////////

import { init as backToTopInit } from "./modules/backtotop.mjs";
import { init as colorSettingsInit } from "./modules/colorsettings.mjs";
import { init as maximizeInit } from "./modules/maximize.mjs";
import { init as foregroundInit } from "./modules/foreground.mjs";
import { init as menuInit } from "./modules/menu.mjs";
import { init as readingSettingsInit } from "./modules/readingsettings.mjs";
import { init as starfieldInit } from "./modules/starfield.mjs";

///////////////////////

window.globals = globals;
window.helpers = helpers;

function initAll() {
	backToTopInit();
	colorSettingsInit();
	maximizeInit();
	foregroundInit();
	menuInit();
	readingSettingsInit();
	starfieldInit();
}
initAll();