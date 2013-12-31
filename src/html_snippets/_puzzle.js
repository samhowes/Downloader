// Copyright (c) 2009 Solve Media Inc.
var _ACPuzzleUtil = _ACPuzzleUtil || {
	callbacks: [],
	puzzle_count: 0,
	puzzles: {},
	add_callback: function (fn, context) {
		var i = this.callbacks.length;
		this.callbacks[i] = function (obj) {
			fn.call(context, obj);
		};
		return i;
	},
	add_puzzle: function (puzzle, id) {
		if (typeof this.get_puzzle(id) == 'undefined') {
			this.puzzle_count++;
		}
		this.puzzles[id] = puzzle;
		return this.puzzle_count;
	},
	get_puzzle: function (id) {
		return this.puzzles[id];
	},
	make_puzzle_id: function () {
		var newid;
		var x = this.puzzle_count;
		do {
			newid = 'acpuz_' + x;
			x++;
		} while (typeof this.get_puzzle(newid) != 'undefined');
		return newid;
	}
}
var ACPuzzleCurrent;

function ACPuzzleObject(opts) {
	var ACPuzzleInfo = opts;
	this.PuzzleInfo = function () {
		return ACPuzzleInfo;
	};
	this.theme = {
		purple: {
			bg: '#5d216b',
			bd: '#2b0833',
			fg: '#fff',
			lk: '#004',
			hv: '#aaa',
			er: '#ff0',
			is: '-puV2',
			ls: '-puV2'
		},
		red: {
			bg: '#c71018',
			bd: '#690f0f',
			fg: '#fff',
			lk: '#004',
			hv: '#aaa',
			er: '#ff0',
			is: '-rdV2',
			ls: '-rdV2'
		},
		black: {
			bg: '#111',
			bd: '#444',
			fg: '#fff',
			lk: '#ccf',
			hv: '#555',
			er: '#f00',
			is: '-bkV2',
			ls: '-bkV2'
		},
		white: {
			bg: '#f8f8f8',
			bd: '#bbb',
			fg: '#000',
			lk: '#004',
			hv: '#aaa',
			er: '#f00',
			is: '-whV2',
			ls: '-whV2'
		},
		none: {
			is: '-bkV2',
			ls: '-whV2'
		},
		custom: {
			is: '-bkV2',
			ls: '-whV2'
		}
	};
	this.locale = {
		"sv": {
			"VISUAL": "Växla till visuell pussel",
			"AUDIO": "Växla till ljud pussel",
			"PLAYING": "Spela ljud",
			"NEWPUZ": "Nya pussel",
			"INFO": "Mer information",
			"CONTINUE": "FORTGÅ",
			"AGAIN": "Försök igen",
			"RETURN": "Återgå till Sida",
			"PROVE": "Bevisa att du är människa för att bekämpa spam",
			"DLAUDIO": "Ladda ner mp3-fil",
			"ANSWER": "Ditt svar",
			"REPLAY": "Lyssna igen"
		},
		"pt": {
			"VISUAL": "Mude para o quebra-cabeça visual",
			"AUDIO": "Mude para o quebra-cabeça de áudio",
			"PLAYING": "Reproduzir som",
			"NEWPUZ": "Novo quebra-cabeça",
			"INFO": "Mais informações",
			"CONTINUE": "CONTINUAR",
			"AGAIN": "Tente novamente",
			"RETURN": "Retornar para Página",
			"PROVE": "Prove que você é um ser humano para ajudar a combater o spam",
			"DLAUDIO": "Baixar arquivo mp3",
			"ANSWER": "A sua resposta",
			"REPLAY": "Ouça novamente"
		},
		"yi": {
			"VISUAL": "באַשטימען צו אַ וויזשאַוואַל רעטעניש",
			"AUDIO": "באַשטימען צו אַן אַודיאָ רעטעניש",
			"PLAYING": "פּלייַינג אַודיאָ",
			"NEWPUZ": "נייַע רעטעניש",
			"INFO": "מער אינפֿאָרמאַציע",
			"CONTINUE": "פאָרזעצן",
			"AGAIN": "פרובירט נאכאמאל",
			"RETURN": "צוריקקומען צו בלאט",
			"PROVE": "באַווייַזן איר ניטאָ מענטש צו העלפן קעמפן ספּאַם",
			"DLAUDIO": "אָפּלאָדירן mp3 טעקע",
			"ANSWER": "דיין ענטפֿער",
			"REPLAY": "הערן ווידער"
		},
		"tr": {
			"VISUAL": "Görsel bulmaca geçiş",
			"AUDIO": "Ses bulmaca geçiş",
			"PLAYING": "Ses çalma",
			"NEWPUZ": "Yeni bulmaca",
			"INFO": "Daha fazla bilgi",
			"CONTINUE": "DEVAM",
			"AGAIN": "Tekrar deneyin",
			"RETURN": "Sayfaya Dön",
			"PROVE": "Eğer mücadele Spam yardımcı olmak için insan olduğunuzu kanıtlamak",
			"DLAUDIO": "Mp3 dosyası indir",
			"ANSWER": "Yanıtınız",
			"REPLAY": "Tekrar dinle"
		},
		"jp": {
			"VISUAL": "目視で確認コードを見る",
			"AUDIO": "オーディオで確認コードを聞く",
			"PLAYING": "オーディオを再生",
			"NEWPUZ": "新しい確認コード",
			"INFO": "詳細...",
			"CONTINUE": "続ける",
			"AGAIN": "再度入力してください",
			"RETURN": "ページに戻る",
			"PROVE": "あなたは戦いのスパムを支援する人間だ証明",
			"DLAUDIO": "mp3ファイルをダウンロードして",
			"ANSWER": "入力欄",
			"REPLAY": "聞き返す"
		},
		"it": {
			"VISUAL": "Cambia ad un puzzle visivo",
			"AUDIO": "Cambia a un puzzle audio",
			"PLAYING": "Riproduzione audio",
			"NEWPUZ": "Nuovo puzzle",
			"INFO": "Maggiori informazioni",
			"CONTINUE": "CONTINUARE",
			"AGAIN": "Riprova",
			"RETURN": "Ritorna alla Pagina",
			"PROVE": "Dimostra che sei umano per aiutare a combattere lo spam",
			"DLAUDIO": "Scaricare file mp3",
			"ANSWER": "Tua risposta",
			"REPLAY": "Ascoltate ancora"
		},
		"hu": {
			"VISUAL": "Váltás vizuális rejtvény",
			"AUDIO": "Váltás hang rejtvény",
			"PLAYING": "Hang lejátszása",
			"NEWPUZ": "Új rejtvény",
			"INFO": "További információ",
			"CONTINUE": "TOVÁBB",
			"AGAIN": "Próbáld újra",
			"RETURN": "Vissza az oldalra",
			"PROVE": "Bizonyítsuk be,hogy ember,hogy segít leküzdeni a spam",
			"DLAUDIO": "Download mp3 fájl",
			"ANSWER": "Az Ön válasza",
			"REPLAY": "Hallgassa újra"
		},
		"es": {
			"VISUAL": "Cambie a un rompecabezas visual",
			"AUDIO": "Cambie a un rompecabezas de audio",
			"PLAYING": "Reproducción de audio",
			"NEWPUZ": "Nuevo rompecabezas",
			"INFO": "Más información",
			"CONTINUE": "CONTINUAR",
			"AGAIN": "Inténtelo de nuevo",
			"RETURN": "Regrese a la Página",
			"PROVE": "Demuestra que eres humano para ayudar a combatir el spam",
			"DLAUDIO": "Descargar el archivo mo3",
			"ANSWER": "Su respuesta",
			"REPLAY": "Escuchar de nuevo"
		},
		"ca": {
			"VISUAL": "Canviar a trencaclosques visual",
			"AUDIO": "Canviar a trencaclosques àudio",
			"PLAYING": "Reproducció d'àudio",
			"NEWPUZ": "Nou trencaclosques",
			"INFO": "Més informació",
			"CONTINUE": "CONTINUAR",
			"AGAIN": "Intenteu-ho de nou",
			"RETURN": "Torneu a la pàgina",
			"PROVE": "Demostra que ets humà per ajudar a combatre el correu brossa",
			"DLAUDIO": "Descarregar arxiu mp3",
			"ANSWER": "La seva reposta",
			"REPLAY": "Escoltar de nou"
		},
		"pl": {
			"VISUAL": "Przełącz do wizualnego łamigłówki",
			"AUDIO": "Przełącz do dźwięku łamigłówki",
			"PLAYING": "Odtwarzanie dźwięku",
			"NEWPUZ": "Nowe łamigłówki",
			"INFO": "Więcej informacji",
			"CONTINUE": "DALEJ",
			"AGAIN": "Spróbuj ponownie",
			"RETURN": "Powrót do Strony",
			"PROVE": "Udowodnij,że jesteś człowiekiem,który pomaga w walce ze spamem",
			"DLAUDIO": "Pobierz plik mp3",
			"ANSWER": "Twoja odpowiedź",
			"REPLAY": "Posłuchaj jeszcze raz"
		},
		"no": {
			"VISUAL": "Bytt til visuell puslespill",
			"AUDIO": "Bytt til lyd puslespill",
			"PLAYING": "Spille lyd",
			"NEWPUZ": "Ny oppgave",
			"INFO": "Mer informasjon",
			"CONTINUE": "FORTSETT",
			"AGAIN": "Prøv igjen",
			"RETURN": "Tilbake til siden",
			"PROVE": "Bevise at du er menneskelig å bidra til å bekjempe spam",
			"DLAUDIO": "Last ned mp3-fil",
			"ANSWER": "Svaret",
			"REPLAY": "Lytt på nytt"
		},
		"nl": {
			"VISUAL": "Overschakelen naar visuele puzzel",
			"AUDIO": "Overschakelen naar geluid puzzel",
			"PLAYING": "Spelen geluid",
			"NEWPUZ": "Nieuwe puzzel",
			"INFO": "Meer informatie",
			"CONTINUE": "VERDER",
			"AGAIN": "Probeer het opnieuw",
			"RETURN": "Terug naar pagina",
			"PROVE": "Bewijzen dat je een mens om spam tegen te gaan zijn",
			"DLAUDIO": "Download mp3 bestand",
			"ANSWER": "Uw antwoord",
			"REPLAY": "Luister opnieuw"
		},
		"en": {
			"VISUAL": "Switch to visual puzzle",
			"AUDIO": "Switch to audio puzzle",
			"MOBTYPE": "Type the phrase to continue:",
			"PLAYING": "Playing",
			"NEWPUZ": "New Puzzle",
			"MOBMENU": "Choose one to continue:",
			"INFO": "More Information...",
			"CONTINUE": "CONTINUE",
			"AGAIN": "Try again",
			"RETURN": "Return to Page",
			"PROVE": "Prove you're human to help fight spam",
			"DLAUDIO": "Download mp3 file",
			"ANSWER": "Your Answer",
			"REPLAY": "Play again"
		},
		"fr": {
			"VISUAL": "Changez à un casse-tête visuel",
			"AUDIO": "Changez à un casse-tête audio",
			"PLAYING": "Lecture des fichiers audio",
			"NEWPUZ": "Nouveau casse-tête",
			"INFO": "Plus d'informations",
			"CONTINUE": "CONTINUER",
			"AGAIN": "Essayez de nouveau",
			"RETURN": "Retour à la Page",
			"PROVE": "Prouvez que vous êtes un être humain pour aider à lutter contre le spam",
			"DLAUDIO": "Télécharger le fichier mp3",
			"ANSWER": "Votre réponse",
			"REPLAY": "Écoutez encore"
		},
		"de": {
			"VISUAL": "Umstellung auf visuelle Puzzle",
			"AUDIO": "Umstellung auf Audio-Puzzle",
			"PLAYING": "Abspielen von Audio",
			"NEWPUZ": "neue Puzzle",
			"INFO": "weitere Informationen zu erhalten...",
			"CONTINUE": "FORTFAHREN",
			"AGAIN": "Nochmals versuchen",
			"RETURN": "Zurück zu Seite",
			"PROVE": "Beweise,dass du ein Mensch bist,um Spam zu bekämpfen",
			"DLAUDIO": "Download mp3-Datei",
			"ANSWER": "Ihre Antwort",
			"REPLAY": "Hören Sie noch einmal"
		},
		"ja": {
			"VISUAL": "目視で確認コードを見る",
			"AUDIO": "オーディオで確認コードを聞く",
			"PLAYING": "オーディオを再生",
			"NEWPUZ": "新しい確認コード",
			"INFO": "詳細...",
			"CONTINUE": "続ける",
			"AGAIN": "再度入力してください",
			"RETURN": "ページに戻る",
			"PROVE": "あなたは戦いのスパムを支援する人間だ証明",
			"DLAUDIO": "mp3ファイルをダウンロードして",
			"ANSWER": "入力欄",
			"REPLAY": "聞き返す"
		}
	};
	this.size = {
		"standard": {
			"w": 300,
			"h": 150
		},
		"520x250": {
			"w": 520,
			"h": 250
		},
		"600x360": {
			"w": 600,
			"h": 360
		},
		"336x280": {
			"w": 336,
			"h": 280
		},
		"300x100": {
			"w": 300,
			"h": 100
		},
		"720x310": {
			"w": 720,
			"h": 310
		},
		"300x150": {
			"w": 300,
			"h": 150
		},
		"600x300": {
			"w": 600,
			"h": 300
		},
		"300x250": {
			"w": 300,
			"h": 250
		}
	};
	this.css = ' #adcopy-outer_ID_{background-color:_BGCOLOR_;color:_FGCOLOR_;border:1px solid _BDCOLOR_;border-radius:4px;-moz-border-radius:4px;-webkit-border-radius:4px;width:_WIDTH_px;padding:3px;margin:0px;} #adcopy-outer_ID_ tbody,#adcopy-outer_ID_ table,#adcopy-outer_ID_ span,#adcopy-outer_ID_ tr,#adcopy-outer_ID_ td,#adcopy-outer_ID_ a,#adcopy-outer_ID_ img{padding:0 !important;margin:0 !important;border:0 !important;line-height:normal !important;} #adcopy-outer_ID_ td{white-space:nowrap !important;} #adcopy-instr_ID_,#adcopy-error-msg_ID_,#adcopy-page-return,#adcopy-expanded-instructions{font-size:10pt;font-family:sans-serif;} #adcopy-instr_ID_{color:_FGCOLOR_;display:inline;} #adcopy-error-msg_ID_{color:_ERCOLOR_;display:none;} #adcopy-outer_ID_ #adcopy-logo_ID_ A:hover{background-color:transparent;} #adcopy-outer_ID_ #adcopy-logo_ID_{color:_FGCOLOR_;display:inline;} #adcopy-outer_ID_ A{color:_LKCOLOR_;text-decoration:none;} #adcopy-link-image_ID_,#adcopy-pixel-image_ID_,#adcopy_challenge_container_ID_{display:none;} #adcopy-outer_ID_ #adcopy-link-logo_ID_ img{vertical-align:middle;} #adcopy-inviz{background:transparent!important;} #adcopy-link-refresh_ID_,#adcopy-link-info_ID_{display:inline;} #adcopy-outer_ID_ #adcopy-link-refresh_ID_ img,#adcopy-outer_ID_ #adcopy-link-info_ID_ img,#adcopy-outer_ID_ #adcopy-link-audio_ID_ img,#adcopy-outer_ID_ #adcopy-link-image_ID_ img{vertical-align:middle;} #adcopy-puzzle-image_ID_{position:relative;height:_HEIGHT_px;width:_WIDTH_px;} #adcopy-puzzle-image_ID_ img{float:none !important;} #adcopy-outer_ID_ #adcopy_response_ID_{width:_WIDTHM115_px !important;margin:2px 0 0 0;font-size:12px;} #adcopy-response-cell_ID_{height:23px;} @-webkit-keyframes adcopy-bouncer{0%,6%,12%,18%,24%,100%{-webkit-transform:translate(0,0);} 3%{-webkit-transform:translate(1px,-10px);} 9%{-webkit-transform:translate(0px,8px);} 15%{-webkit-transform:translate(0px,-5px);} 21%{-webkit-transform:translate(1px,2px);} } @-moz-keyframes adcopy-bouncer{0%,6%,12%,18%,24%,100%{-moz-transform:translate(0,0);} 3%{-moz-transform:translate(1px,-10px);} 9%{-moz-transform:translate(0px,8px);} 15%{-moz-transform:translate(0px,-5px);} 21%{-moz-transform:translate(1px,2px);} } .adcopy-info-bouncy img{-webkit-animation:adcopy-bouncer 2s infinite;-moz-animation:adcopy-bouncer 2s infinite;} .adcopy-info-bouncy img:hover{-webkit-animation:none;-moz-animation:none;} #adcopy-lightbox_ID_{z-index:1000;background:rgba(13,13,13,0.5);position:fixed;height:100%;width:100%;top:0;left:0;} #adcopy-outer_ID_.ac-expanded{margin:auto;position:fixed;width:auto;z-index:5000;padding:6px 10px;} #adcopy-outer_ID_.ac-expanded iframe{height:100%;width:100%;} #adcopy-outer_ID_.ac-expanded #adcopy-link-buttons-container_ID_{display:none;} #adcopy-outer_ID_.ac-expanded #adcopy_response_ID_{width:400px!important;} #adcopy-outer_ID_.ac-expanded #adcopy-puzzle-image_ID_{border:1px solid _BDCOLOR_;} #adcopy-outer_ID_.ac-expanded #adcopy-page-return_ID_{background:url(\'_MEDIA_/btn_SUFFIX_.gif\');color:white;width:120px;height:30px;display:inline-block;line-height:30px!important;border-radius:4px;-moz-border-radius:4px;-webkit-border-radius:4px;} #adcopy-outer_ID_.ac-expanded #adcopy-instr_ID_,#adcopy-outer_ID_.ac-expanded #adcopy-error-msg_ID_{font-size:14px;line-height:20px!important;} #adcopy-outer_ID_.ac-expanded #adcopy_response_ID_{font-size:16px;} #adcopy-outer_ID_.ac-expanded #adcopy-expanded-instructions_ID_{font-weight:bold;font-size:16px;line-height:24px!important;} #adcopy-outer_ID_.ac-expanded #adcopy-instr-row_ID_{height:26px;} ';
	this.html = ' %3Cdiv id%3D"adcopy-outer_ID_"%3E %3Ctable cellpadding%3D0 cellspacing%3D0%3E %3Ctr%3E%3Ctd colspan%3D3%3E%3Cdiv id%3D"adcopy-puzzle-image_ID_"%3E%3C%2Fdiv%3E %3C%2Ftd%3E%3C%2Ftr%3E %3Ctr id%3D"adcopy-instr-row_ID_"%3E%3Ctd%3E%3Cspan id%3D"adcopy-instr_ID_"%3E_ANSWER_%3C%2Fspan%3E%3Cspan id%3D"adcopy-error-msg_ID_"%3Eerror%3C%2Fspan%3E%3C%2Ftd%3E %3Ctd%3E%3Cdiv id%3D"adcopy-pixel-image_ID_" style%3D"display:none;"%3E%3C%2Fdiv%3E%3C%2Ftd%3E %3Ctd align%3D"center"%3E%3Cspan id%3D"adcopy-logo_ID_"%3E%3Ca href%3D"javascript:ACPuzzle.moreinfo(\%27_JSID_\%27)" id%3D"adcopy-link-logo_ID_" title%3D"" %3E%3Cimg src%3D"_MEDIA_%2Fsolve_LOGOSUFFIX_.png" alt%3D"Solve Media"%3E%3C%2Fa%3E%3C%2Fspan%3E%3C%2Ftd%3E %3C%2Ftr%3E %3Ctr%3E %3Ctd id%3D"adcopy-response-cell_ID_"%3E%3Cinput type%3Dtext name%3D"adcopy_response" id%3D"adcopy_response_ID_" size%3D20 autocomplete%3D"off" autocorrect%3D"off"%3E%3Cspan id%3D"adcopy_challenge_container_ID_"%3E%3Cinput type%3Dhidden name%3D"adcopy_challenge" id%3D"adcopy_challenge_ID_"%3E%3C%2Fspan%3E%3C%2Ftd%3E %3Ctd%3E%3C%2Ftd%3E %3Ctd align%3D"center" id%3D"adcopy-link-buttons_ID_"%3E%3Cspan id%3D"adcopy-link-buttons-container_ID_"%3E%3Ca href%3D"javascript:ACPuzzle.reload(\%27_JSID_\%27)" id%3D"adcopy-link-refresh_ID_" title%3D"_NEWPUZ_"%3E%3Cimg src%3D"_MEDIA_%2Freload_SUFFIX_.gif" alt%3D"_NEWPUZ_"%3E%3C%2Fa %3E%3Ca href%3D"javascript:ACPuzzle.change2audio(\%27_JSID_\%27)" id%3D"adcopy-link-audio_ID_" title%3D"_AUDIO_" %3E%3Cimg src%3D"_MEDIA_%2Fnote_SUFFIX_.gif" alt%3D"_AUDIO_"%3E%3C%2Fa %3E%3Ca href%3D"javascript:ACPuzzle.change2image(\%27_JSID_\%27)" id%3D"adcopy-link-image_ID_" title%3D"_VISUAL_"%3E%3Cimg src%3D"_MEDIA_%2Ftext_SUFFIX_.gif" alt%3D"_VISUAL_"%3E%3C%2Fa %3E%3Ca href%3D"javascript:ACPuzzle.moreinfo(\%27_JSID_\%27)" id%3D"adcopy-link-info_ID_" title%3D"_INFO_" %3E%3Cimg src%3D"_MEDIA_%2Finfo_SUFFIX_.gif" alt%3D"_INFO_"%3E%3C%2Fa%3E%3C%2Fspan%3E%3C%2Ftd%3E %3C%2Ftr%3E %3C%2Ftable%3E %3C%2Fdiv%3E ';
	this.players = {};
	this._ah = function () {
		var img = this.byid('adcopy-puzzle-image');
		var size = this.size[ACPuzzleInfo.size];
		img.innerHTML = '<div style="width:' + size.w + 'px;"><b>script,html,or compat error</b></div>';
		var mln = this._bl('adcopy_media_listener');
		if (window[mln]) {
			try {
				delete window[mln];
			} catch (e) {
				window[mln] = undefined;
			}
		}
	};
	this._ai = function () {
		var type = ACPuzzleInfo.mediatype;
		var func = this.players[type];
		var size = this.size[ACPuzzleInfo.size];
		var err;
		this.byid('adcopy-link-audio').style.display = 'inline';
		this.byid('adcopy-link-image').style.display = 'none';
		if (!func) {
			var img = this.byid('adcopy-puzzle-image');
			img.innerHTML = '<div style="width:' + size.w + 'px;"><b>ERROR:unknown media type "' + type + '" - cannot display</b></div>';
			return;
		}
		func.call(this);
	};
	this.addEvent = (function () {
		if (window.addEventListener) {
			return function (element, event, func) {
				element.addEventListener(event, func, false);
			};
		} else {
			return function (element, event, func) {
				element.attachEvent('on' + event, func);
			};
		}
	})();
	this.removeEvent = (function () {
		if (window.removeEventListener) {
			return function (element, event, func) {
				element.removeEventListener(event, func, false);
			};
		} else {
			return function (element, event, func) {
				element.detachEvent('on' + event, func);
			};
		}
	})();
	this._aj = function (e) {
		if (e.preventDefault) {
			e.preventDefault();
		} else if (window.event && window.event.returnValue) {
			window.event.returnValue = false;
		}
		return false;
	};
	this._ak = function (id) {
		var mln = this._bl('adcopy_media_listener');
		var l = window[mln];
		return l || (function () {
			var set_master_function, lstnr, do_media_event, target, supported_events, i, e, len;
			if (id) {
				target = document.getElementById(id);
			}
			lstnr = {};
			lstnr.name = mln;
			do_media_event = function (event) {
				var funcs = lstnr[event].funcs;
				for (var func in funcs) {
					if (funcs[func]) {
						funcs[func].call(lstnr, target);
					}
				}
			};
			supported_events = ["update", "started", "finished", "init", "error"];
			set_master_function = function (e) {
				lstnr[e] = function () {
					do_media_event(e);
				};
				lstnr[e].funcs = [];
			};
			for (i = 0, len = supported_events.length; i < len; i++) {
				e = supported_events[i];
				set_master_function(e);
			}
			lstnr.addEvent = function (event, func) {
				return (lstnr[event].funcs.push(func)) - 1;
			};
			lstnr.removeEvent = function (event, index) {
				lstnr[event].funcs[index] = null;
			};
			lstnr.setTarget = function (el) {
				target = el;
			};
			window[mln] = lstnr;
			return lstnr;
		})();
	};
	this.players.error = function () {
		var img = this.byid('adcopy-puzzle-image');
		img.innerHTML = '';
		var func = ACPuzzleInfo.onerror;
		if (func) func.call(this);
	};
	this.players.img = function () {
		var url = this.media_url();
		var size = this.size[ACPuzzleInfo.size];
		var img = this.byid('adcopy-puzzle-image');
		var iid = this._bl('adcopy-puzzle-image-image');
		img.innerHTML = '<img src="' + url + '" alt="Solve Media Puzzle Challenge" height="' + size.h + '" width="' + size.w + '" id="' + iid + '"/>';
	};
	this.players.imgmap = function () {
		var url = this.media_url();
		var size = this.size[ACPuzzleInfo.size];
		var img = this.byid('adcopy-puzzle-image');
		var iid = this._bl('adcopy-puzzle-image-image');
		var mid = 'adcopy-map-unique-' + new Date().getTime();
		var opt = this._am();
		var n;
		var area = '';
		var tgt = '_NEW-' + new Date().getTime();
		for (n = 0; n < opt.length; n++) {
			area = area + '<area shape="' + opt[n].shape + '" coords="' + opt[n].coords + '" href="' + this._bw(opt[n].href) + '" alt="' + opt[n].alt + '" title="' + opt[n].alt + '" target="' + tgt + '"/>';
		}
		img.innerHTML = '<img src="' + url + '" height="' + size.h + '" width="' + size.w + '" id="' + iid + '" usemap="#' + mid + '"/>' + '<map name="' + mid + '">' + area + '</map>';
	};
	this.players.aud = function () {
		var url = this.media_url();
		var width = this.size[ACPuzzleInfo.size].w;
		var height = this.size[ACPuzzleInfo.size].h;
		var media = this._bv() + '/media';
		var o = this.byid('adcopy-puzzle-image');
		var lang = this.locale[ACPuzzleInfo.lang] || this.locale.en;
		if (/ua\/msie/.test(ACPuzzleInfo.caps)) {
			var match = new RegExp('^(http[s]?:)?/' + '/api(-secure)?', 'i');
			url = url.replace(match, 'http:/' + '/api');
		}
		if (/swf/.test(ACPuzzleInfo.caps)) {
			var self = this;
			var mln = this._ak();
			var pswf = ' <object type="application/x-shockwave-flash" data="_MEDIA_/smflashplayer.swf" id="_OBJID_" name="_OBJID_" height="_HEIGHT_" width="_WIDTH_"> <param name="wmode" value="transparent" /> <param name="movie" value="_MEDIA_/smflashplayer.swf"/> <param name="allowscriptaccess" value="always"/> <param name="FlashVars" value="mediatype=audio&amp;autostart=true&amp;media=_MEDIA_&amp;url=_URL_&amp;type=mp3&amp;listener=_LISTENER_&amp;width=_WIDTH_&amp;height=_HEIGHT_" /> </object> ';
			var css = ' #adcopy-puzzle-audio-rewind_ID_,#adcopy-puzzle-audio-playing_ID_{position:absolute;left:-5000px;} ';
			var objid = this._bl('adcopy-puzzle-audio');
			var rewid = this._bl('adcopy-puzzle-audio-rewind');
			var playingid = this._bl('adcopy-puzzle-audio-playing');
			var replace_placeholders = function (x) {
				x = x.replace(/_URL_/g, url);
				x = x.replace(/_ID_/g, self._bm());
				x = x.replace(/_WIDTH_/g, width);
				x = x.replace(/_HEIGHT_/g, height);
				x = x.replace(/_MEDIA_/g, media);
				x = x.replace(/_OBJID_/g, objid);
				x = x.replace(/_LISTENER_/g, mln.name);
				return x;
			};
			o.innerHTML = replace_placeholders(pswf);
			this._cc(replace_placeholders(css));
			var playing = document.createElement("span");
			playing.id = playingid;
			playing.innerHTML = lang.PLAYING;
			var replay = document.createElement("a");
			replay.href = "#";
			replay.id = rewid;
			replay.innerHTML = lang.REPLAY;
			mln.addEvent('started', function () {
				self.byid('adcopy_response').focus();
				if (replay.parentNode === o) {
					o.removeChild(replay);
				}
				o.appendChild(playing);
			});
			mln.addEvent('finished', function () {
				if (playing.parentNode === o) {
					o.removeChild(playing);
				}
				o.appendChild(replay);
			});
			self.addEvent(replay, 'click', function (e) {
				var audio = self.byid('adcopy-puzzle-audio');
				audio.rewind_media();
				return self._aj(e);
			});
		} else {
			o.innerHTML = '<div style="width:' + width + 'px;"></div>';
			var a = '<div style="width:' + width + 'px;"><a style="text-decoration:underline;" href="' + url + ';aa=1">' + lang.DLAUDIO + '</a></div>';
			setTimeout(function () {
				o.innerHTML = a;
			}, 250);
		}
		o.height = height;
		this.byid('adcopy-link-audio').style.display = 'none';
		this.byid('adcopy-link-image').style.display = 'inline';
	};
	this._al = function () {
		var opt = ACPuzzleInfo.widget.player || {};
		if (opt.hasOwnProperty('player_opts')) {
			opt = opt.player_opts;
		}
		return opt;
	};
	this._am = function () {
		var opt = ACPuzzleInfo.widget.player || {};
		if (opt.hasOwnProperty('click_zones')) {
			opt = opt.click_zones;
		}
		return opt;
	};
	this._an = function (zones, map_id, replay_func, play_func, dest_size) {
		var tgt, n, area, zone, map, match, f, msize, scale;
		var self = this;
		msize = ACPuzzleInfo.media_size;
		scale = {
			x: (dest_size.w / msize.w),
			y: (dest_size.h / msize.h)
		};
		tgt = '_NEW-' + new Date().getTime();
		map = document.createElement('map');
		map.id = map_id;
		map.name = map_id;
		for (n = 0; n < zones.length; n++) {
			zone = zones[n];
			zone.coords = zone.coords.match(/((poster|middle|last):)?(.*)/).pop();
			if (scale.x !== 1 || scale.y !== 1) {
				zone.coords = (function (s, c) {
					var i, l, newc;
					newc = [];
					coord = c.split(/,/);
					if (s === "circle") {
						/*
If the scale factor isn't even on both dimensions,we can scale a rectangle into a square no problem.
Since we can't make a circle into an oval,we try
the next best thing;scale up the radius using the
average of the x and y scale factors. In real
life,I'm not sure how often we would scale to odd
dimensions or use circles for click zones,but...
*/
						newc[0] = coord[0] * scale.x;
						newc[1] = coord[1] * scale.y;
						newc[2] = coord[2] * ((scale.x + scale.y) / 2);
					} else {
						for (i = 0, l = coord.length; i < l; i++) {
							if (i % 2 === 0) {
								newc[i] = coord[i] * scale.x;
							} else {
								newc[i] = coord[i] * scale.y;
							}
						}
					}
					return newc.join(',');
				})(zone.shape, zone.coords);
			}
			area = document.createElement('area');
			area.shape = zone.shape;
			area.coords = zone.coords;
			area.alt = zone.alt;
			area.title = zone.alt;
			match = zone.href.match(/^\{ac:video((re)?play)\}/);
			if (match) {
				area.href = "#";
				switch (match[1]) {
				case "replay":
					f = replay_func;
					break;
				case "play":
					f = play_func;
					break;
				}
				self.addEvent(area, 'click', function (e) {
					f.call();
					return self._aj(e);
				});
				map.insertBefore(area, map.firstChild);
			} else {
				area.href = self._bw(zone.href);
				area.target = tgt;
				map.appendChild(area);
			}
		}
		return map;
	};
	this._ao = function (api) {
		var media = this._bv();
		var size = this.size[ACPuzzleInfo.size];
		var msize = ACPuzzleInfo.media_size;
		var img = this.byid('adcopy-puzzle-image');
		var iid = this._bl('adcopy-puzzle-image-image');
		var opt = this._al();
		var vl;
		var video;
		var self = this;
		img.innerHTML = "";
		video = api.videoElement;
		vl = api.listener;
		if (opt) {
			if (opt.autostart && !opt.poster) {
				api.autoplay(video);
			}
			if (opt.loop && !opt.endcard) {
				api.loop(video);
			}
			if (opt.poster) {
				var poster = document.createElement('img');
				poster.src = media + opt.poster;
				poster.style.cssText = 'height:100%!important;' + 'width:100%!important;' + 'padding:0!important;' + 'margin:0!important;' + 'border:0!important;' + 'z-index:2!important;';
				poster.height = size.h;
				poster.width = size.w;
				poster.id = self._bl("adcopy-poster");
				vl.addEvent('init', function () {
					api.hide();
					video.parentNode ? img.insertBefore(poster, video) : img.appendChild(poster);
				});
			}
			if (opt.endcard) {
				var endcard = document.createElement("img");
				endcard.src = media + opt.endcard;
				endcard.style.cssText = 'height:100%!important;' + 'width:100%!important;' + 'padding:0!important;' + 'margin:0!important;' + 'border:0!important;' + 'z-index:2!important;';
				endcard.id = this._bl('adcopy-endcard');
				vl.addEvent('finished', function () {
					api.hide();
					img.insertBefore(endcard, video);
				});
			}
		}
		vl.addEvent('error', function () {
			img.insertBefore(endcard, video);
			video.parentNode.removeChild(video);
			if (poster && poster.parentNode === img) {
				poster.parentNode.removeChild(poster);
			}
		});
		if (msize && (msize.h !== size.h || msize.w !== size.w)) {
			vl.addEvent('started', function () {
				self._aq(msize.h, msize.w, function () {
					api.expanded = true;
					api.set_area();
				}, function () {
					api.expanded = false;
					api.set_area();
				});
			});
		}
		img.appendChild(video);
		vl.setTarget(video);
	};
	this._ap = function (api) {
		var pixel_pointer = 0;
		var imgmap, z, zone, n, area, prefix, comp, mask, map_el;
		var set_pixels, replay, fire_pixel, play;
		var mid = 'adcopy-map-unique-' + new Date().getTime();
		var z_data = this._am();
		var zones = {
			'poster': [],
			'middle': [],
			'last': []
		};
		var completions = [];
		var img = this.byid('adcopy-puzzle-image');
		var iid = this._bl('adcopy-puzzle-image-image');
		var size = this.size[ACPuzzleInfo.size];
		var media = this._bv() + '/media';
		var use_gif = false;
		var msize = ACPuzzleInfo.media_size;
		var self = this;
		var vl = self._ak();
		var video = document.getElementById(iid);
		api.set_area = function (frame) {
			var old_map;
			if (frame) {
				api.current_frame = frame;
			} else {
				frame = api.current_frame;
			}
			if (api.expanded) {
				frame = frame + "-exp";
			}
			old_map = img.getElementsByTagName("map")[0];
			if (old_map) {
				img.replaceChild(zones[frame].map, old_map);
			} else {
				img.appendChild(zones[frame].map);
			}
		};
		fire_pixel = function (pixel) {
			var url = self._bw(pixel.href);
			var img = document.createElement("img");
			img.src = url;
		};
		set_pixels = function () {
			var complen = completions.length;
			var l = vl.addEvent('update', function () {
				var duration = api.duration();
				var pct_complete = (api.currentTime() / duration) * 100;
				if (pixel_pointer < complen && pct_complete >= completions[pixel_pointer].coords) {
					fire_pixel(completions[pixel_pointer]);
					pixel_pointer = pixel_pointer + 1;
				}
				if (pixel_pointer == complen) {
					vl.removeEvent('update', l);
					pixel_pointer = 0;
				}
			});
			var f = vl.addEvent('finished', function () {
				if (pixel_pointer > 0) {
					for (pixel_pointer; pixel_pointer < complen; pixel_pointer = pixel_pointer + 1) {
						fire_pixel(completions[pixel_pointer]);
					}
				}
				vl.removeEvent('finished', f);
			});
		};
		for (z = 0; z < z_data.length; z++) {
			zone = z_data[z];
			prefix = zone.coords.split(':')[0];
			if (zones[prefix]) {
				zones[prefix].push(zone);
			} else if (prefix === "complete") {
				zone.coords = zone.coords.replace('complete:', '');
				completions.push(zone);
			}
		}
		completions.sort(function (a, b) {
			return a.coords - b.coords;
		});
		set_pixels();
		replay = function () {
			var endcard = self.byid('adcopy-endcard');
			set_pixels();
			if (endcard) {
				img.removeChild(endcard);
			}
			api.show();
			api.rewind();
		};
		play = function () {
			var poster = self.byid('adcopy-poster');
			if (poster) {
				img.removeChild(poster);
			}
			api.show();
			api.play();
		};
		for (n in zones) {
			if (zones.hasOwnProperty(n)) {
				if (msize && (msize.h !== size.h || msize.w !== size.w)) {
					zones[n + "-exp"] = {};
					zones[n + "-exp"].map = self._an(zones[n], mid, replay, play, msize);
				}
				zones[n].map = self._an(zones[n], mid, replay, play, size);
			}
		}
		mask = document.createElement('img');
		mask.id = this._bl("adcopy-inviz");
		mask.style.cssText = 'width:100%!important;' + 'height:100%!important;' + 'padding:0!important;' + 'margin:0!important;' + 'border:0!important;' + 'position:absolute!important;' + 'z-index:3!important;';
		mask.width = size.w;
		mask.height = size.h; /*@cc_on @*/
		/*@if(@_jscript_version < 5.8)use_gif=true;@end @*/
		if (use_gif) {
			mask.src = media + "/blank.gif";
		} else {
			this.addEvent(mask, "error", function () {
				if (mask.width !== 1 || mask.height !== 1) {
					mask.src = media + "/blank.gif";
				}
			});
			mask.src = "data:image/gif;base64,R0lGODlhAQABAIAAAP\/\/\/\/\/\/\/yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
		}
		mask.useMap = '#' + mid;
		img.insertBefore(mask, img.firstChild);
		api.set_area('poster');
		vl.addEvent('started', function () {
			api.set_area('middle');
		});
		vl.addEvent('finished', function () {
			api.set_area('last');
		});
		vl.addEvent('error', function () {
			img.removeChild(mask);
		});
	};
	this.players.vid = function () {
		var url = this.media_url();
		var size = this.size[ACPuzzleInfo.size];
		var iid = this._bl('adcopy-puzzle-image-image');
		var self = this;
		var vl = self._ak();
		var video = document.createElement('video');
		var source = document.createElement('source');
		source.src = url;
		video.appendChild(source);
		video.setAttribute('webkit-playsinline', "webkit-playsinline");
		video.style.cssText = 'height:100%!important;' + 'width:100%!important;' + 'padding:0!important;' + 'border:0!important;' + 'margin:0!important;' + 'z-index:1!important;';
		video.height = size.h;
		video.width = size.w;
		video.id = iid;
		var api = {
			listener: vl,
			videoElement: video,
			duration: function () {
				return api.videoElement.duration;
			},
			play: function () {
				return api.videoElement.play();
			},
			paused: function () {
				return api.videoElement.paused;
			},
			pause: function () {
				return api.videoElement.pause();
			},
			currentTime: function () {
				return api.videoElement.currentTime;
			},
			setCurrentTime: function (t) {
				return api.videoElement.currentTime = t;
			},
			rewind: function () {
				api.setCurrentTime(0);
				return api.play();
			},
			hide: function () {
				var video = api.videoElement;
				if (video.style.setProperty) {
					video.style.setProperty('display', 'none', 'important');
				} else {
					video.style.display = "none";
				}
			},
			show: function () {
				api.videoElement.style.display = "";
			},
			autoplay: function () {
				api.videoElement.autoplay = 'autoplay';
			},
			loop: function () {
				api.videoElement.loop = "loop";
			}
		};
		self.addEvent(video, 'canplaythrough', vl.init);
		self.addEvent(video, 'playing', vl.started);
		self.addEvent(video, 'timeupdate', vl.update);
		self.addEvent(video, 'ended', vl.finished);
		self.addEvent(source, 'error', vl.error);
		self.addEvent(video, 'pause', function () {
			if (!video.ended && video.parentElement) {
				video.play();
			}
		});
		this._ao(api);
		return api;
	};
	this.players.vidmap = function () {
		var api = this.players.vid.call(this);
		var vl = api.listener;
		this._ap(api);
	};
	this.players.swf = function () {
		var url = this.media_url();
		var size = this.size[ACPuzzleInfo.size];
		var img = this.byid('adcopy-puzzle-image');
		var iid = this._bl('adcopy-puzzle-image-image');
		var fv = 'url=' + encodeURI(window.location.href) + '&amp;clickTAG=' + encodeURI(this._bt());
		if (ACPuzzleInfo.caps.match(/ua\/firefox/)) {
			img.innerHTML = '<embed type="application/x-shockwave-flash" ' + 'src="' + url + '" ' + 'style="width:' + size.w + 'px;height:' + size.h + 'px;padding:0;margin:0;" id="' + iid + '" ' + 'wmode="opaque" ' + 'FlashVars="' + fv + '" />';
		} else {
			img.innerHTML = '<object type="application/x-shockwave-flash" ' + (ACPuzzleInfo.caps.match(/ua\/msie/) ? ' ' : 'data="' + url + '" ') + 'style="width:' + size.w + 'px;height:' + size.h + 'px;padding:0;margin:0;" id="' + iid + '">' + '<param name="movie" value="' + url + '"/>' + '<param name="FlashVars" value="' + fv + '"/>' + '<param name="wmode" value="opaque">' + '</object>';
		}
	};
	this.players.flv = function () {
		var url = this.media_url();
		var size = this.size[ACPuzzleInfo.size];
		var iid = this._bl('adcopy-puzzle-image-image');
		var self = this;
		var vl = this._ak();
		var objstr, div, video;
		var media = self._bv() + '/media';
		objstr = '<object type="application/x-shockwave-flash" ' + 'height="' + size.h + '" width="' + size.w + '" id="' + iid + '" name="' + iid + '" data="_MEDIA_/smflashplayer.swf" >' + '<param name="wmode" value="opaque"/>' + '<param name="allowscriptaccess" value="always" />' + '<param name="movie" value="_MEDIA_/smflashplayer.swf"/>' + '<param name="FlashVars" value="listener=' + vl.name + '&amp;url=' + encodeURI(url) + '&amp;mediatype=video' + '&amp;interval=500&amp;width=' + size.w + '&amp;height=' + size.h + '"/></object>';
		objstr = objstr.replace(/_MEDIA_/g, media);
		div = document.createElement('div');
		div.innerHTML = objstr;
		video = div.firstChild;
		var api = {
			listener: vl,
			videoElement: video,
			duration: function () {
				return api.videoElement.duration();
			},
			play: function () {
				return api.videoElement.play_media();
			},
			pause: function () {
				return api.videoElement.pause_media();
			},
			paused: function () {
				return api.videoElement.paused();
			},
			currentTime: function () {
				return api.videoElement.currentTime();
			},
			setCurrentTime: function (t) {
				api.videoElement.setPosition(t);
				return api.currentTime();
			},
			rewind: function () {
				return api.videoElement.rewind_media();
			},
			hide: function () {
				var video = api.videoElement;
				if (video.style.setProperty) {
					video.style.setProperty('width', '0', 'important');
					video.style.setProperty('height', '0', 'important');
				} else {
					video.style.width = 0;
					video.style.height = 0;
				}
			},
			show: function () {
				if (video.style.setProperty) {
					video.style.setProperty('width', "100%", 'important');
					video.style.setProperty('height', "100%", 'important');
				} else {
					video.style.width = "100%";
					video.style.height = "100%";
				}
			},
			autoplay: function () {
				vl.addEvent('init', function () {
					api.play();
				});
			},
			loop: function () {
				vl.addEvent('finished', function () {
					api.rewind();
				});
			}
		};
		this._ao(api);
		return api;
	};
	this._aq = function (newH, newW, expandCallback, hideCallback) {
		var self = this;
		var lang = this.locale[ACPuzzleInfo.lang] || this.locale.en;
		var expandClass, classRxp, aco, dummy, img, size, lb, setsize, keepcenter, hidePopup, btns, ret, inst;
		expandClass = "ac-expanded";
		classRxp = new RegExp("\\b" + expandClass + "\\b");
		aco = self.byid('adcopy-outer');
		if (classRxp.test(aco.className)) {
			return;
		}
		dummy = document.createElement('div');
		img = self.byid('adcopy-puzzle-image');
		size = this.size[ACPuzzleInfo.size];
		lb = document.createElement('div');
		btns = self.byid('adcopy-link-buttons');
		ret = document.createElement('a');
		ret.setAttribute("id", self._bl('adcopy-page-return'));
		ret.setAttribute('href', "#");
		ret.innerHTML = lang.RETURN;
		btns.appendChild(ret);
		inst = document.createElement('span');
		inst.setAttribute("id", self._bl('adcopy-expanded-instructions'));
		inst.innerHTML = lang.PROVE + ":";
		aco.insertBefore(inst, aco.firstChild);
		setsize = function (el, height, width) {
			el.style.setProperty('height', height + 'px', 'important');
			el.style.setProperty('width', width + 'px', 'important');
		};
		keepcenter = function () {
			var t = (window.innerHeight - aco.offsetHeight) / 2;
			var l = (window.innerWidth - aco.offsetWidth) / 2;
			aco.style.setProperty('top', '' + t + "px");
			aco.style.setProperty('left', '' + l + "px");
		};
		hidePopup = function (ev) {
			if (ev) {
				self.cancelDefault(ev);
			}
			btns.removeChild(ret);
			aco.removeChild(inst);
			setsize(img, size.h, size.w);
			aco.className = aco.className.replace(classRxp, '');
			aco.style.setProperty('top', '');
			aco.style.setProperty('left', '');
			lb.parentNode.removeChild(lb);
			dummy.parentNode.removeChild(dummy);
			self.removeEvent(window, "resize", keepcenter);
			if (hideCallback) {
				hideCallback();
			}
		};
		lb.setAttribute('id', self._bl("adcopy-lightbox"));
		self.addEvent(lb, 'click', function (ev) {
			ev.stopPropagation();
			if (ev.target === lb) {
				hidePopup();
			}
		}); /* Respond to escape and enter keys */
		self.addEvent(window, 'keydown', function escape(ev) {
			if (ev.keyCode === 27 || ev.keyCode === 13 || ev.keyCode === 9) {
				if (ev.keyCode !== 9) {
					self._aj(ev);
				}
				self.removeEvent(window, 'keydown', escape);
				hidePopup();
			}
		});
		self.addEvent(ret, 'click', function () {
			hidePopup();
		});
		dummy.setAttribute('id', self._bl('adcopy-dummy'));
		dummy.style.height = '' + aco.offsetHeight + 'px';
		dummy.style.width = '' + aco.offsetWidth + 'px';
		aco.className = [expandClass, aco.className].join(' ');
		setsize(img, newH, newW);
		aco.parentNode.insertBefore(lb, aco);
		aco.parentNode.insertBefore(dummy, aco);
		keepcenter();
		self.addEvent(window, "resize", keepcenter);
		if (expandCallback) {
			expandCallback();
		}
	};
	this.players.flvmap = function () {
		var api = this.players.flv.call(this);
		this._ap(api);
	};
	this.players.js = function () {
		var url = this.media_url();
		this._bp(url);
	};
	this.players.html = function () {
		var url = this.media_url();
		var size = this.size[ACPuzzleInfo.size];
		var img = this.byid('adcopy-puzzle-image');
		var iid = this._bl('adcopy-puzzle-image-image');
		var rid = 'adcopy-unique-' + new Date().getTime();
		img.innerHTML = '<div id="' + iid + '"><iframe src="' + url + '" height="' + size.h + '" width="' + size.w + '" id="' + rid + '" frameborder="0" scrolling="no"></iframe></div>';
	};
	this._ar = function () {
		var caps = 'js';
		var ctx = this;
		var fwid = function (x) {
			return ctx._br(26, x) + 97
		};
		/* IE Document mode reports what version IE is or is simulating:* 5 - Quirks Mode
		 * 7,8.9,10 - Self explanatory
		 */
		var ie_doc_mode = (function () {
			if (document.documentMode) {
				return document.documentMode;
			} else {
				return undefined;
			}
		})();
		var c = document.createElement('canvas');
		if (c.getContext) {
			caps = caps + ',h5c';
			if (typeof c.getContext('2d').fillText == 'function') caps = caps + ',h5ct';
		}
		if (document.implementation.hasFeature("http:/" + "/www.w3.org/TR/SVG11/feature#BasicStructure", "1.1")) {
			caps = caps + ',svg';
		}
		var bad_ie9 = false;
		var v = document.createElement('video'); /*@cc_on @*/
		/*@if(@_jscript_version==9)try{v.canPlayType("");} catch(e){bad_ie9=true;}
@end @*/
		if (!bad_ie9 && v.canPlayType) {
			caps = caps + ',h5v';
			if (v.canPlayType('video/mp4;codecs="avc1.42E01E,mp4a.40.2"')) caps = caps + ',v/h264';
			if (v.canPlayType('video/ogg;codecs="theora,vorbis"')) caps = caps + ',v/ogg';
			if (v.canPlayType('video/3gpp;codecs="mp4v.20.8,samr"')) caps = caps + ',v/3gpp';
			if (v.canPlayType('video/webm;codecs="vp8.0,vorbis"')) caps = caps + ',v/webm';
		}
		var a = document.createElement('audio');
		if (!bad_ie9 && a.canPlayType) {
			caps = caps + ',h5a';
			if (a.canPlayType('audio/mpeg')) caps = caps + ',a/mp3';
			if (a.canPlayType('audio/ogg;codecs="vorbis"')) caps = caps + ',a/ogg';
		}
		if (typeof (document.createTouch) != "undefined" || window.navigator.msMaxTouchPoints) {
			caps += ',touch';
		}
		var ua = navigator.userAgent.toLowerCase();
		var bs = [{
			"match": "opera",
			"vermatch": "version/"
		}, {
			"match": "iphone",
			"vermatch": "version/"
		}, {
			"match": "ipad",
			"vermatch": "version/"
		}, {
			"match": "chrome"
		}, {
			"match": "android"
		}, {
			"match": "safari",
			"vermatch": "version/"
		}, {
			"vers": 8,
			"value": "msie",
			"match": "trident/4"
		}, {
			"vers": 9,
			"value": "msie",
			"match": "trident/5"
		}, {
			"vers": 10,
			"value": "msie",
			"match": "trident/6"
		}, {
			"match": "msie"
		}, {
			"match": "firefox"
		}, {
			"match": "mozilla"
		}];
		var os = [{
			match: 'iphone os',
			value: 'iphone'
		}, {
			match: 'iphone;',
			value: 'iphone',
			verunk: 1
		}, {
			match: 'ipad;' + ' cpu',
			value: 'ipad'
		}, {
			match: 'ipad;' + ' u;',
			value: 'ipad'
		}, {
			match: 'ipad;',
			value: 'ipad',
			verunk: 1
		}, {
			match: 'android',
			value: 'android'
		}, {
			match: 'windows nt',
			value: 'nt',
			variants: [{
				match: ' arm;',
				value: 'rt'
			}, {
				match: ' tablet pc',
				value: 'tab'
			}]
		}, {
			match: 'windows phone os',
			value: 'winphone'
		}, {
			match: 'windows phone',
			value: 'winphone'
		}, {
			match: 'mac os x',
			value: 'mac'
		}];
		for (var i = 0; i < bs.length; i++) {
			var idx = ua.indexOf(bs[i].match);
			if (idx == -1) continue;
			var uam = bs[i].value || bs[i].match;
			var vers;
			caps = caps + ',ua/' + uam;
			if (bs[i].vers) {
				vers = bs[i].vers;
			} else if (bs[i].vermatch) {
				var vi = ua.indexOf(bs[i].vermatch);
				if (vi != -1) {
					vers = parseInt(ua.substr(vi + bs[i].vermatch.length));
				}
			} else {
				vers = parseInt(ua.substr(idx + bs[i].match.length + 1));
			}
			if (vers) caps = caps + ',ua/' + uam + vers;
			break;
		}
		for (var i = 0; i < os.length; i++) {
			var idx = ua.indexOf(os[i].match);
			if (idx == -1) continue;
			var osn = os[i].value || os[i].match;
			caps = caps + ',os/' + osn;
			if (os[i].verunk) break;
			var vst = ua.substr(idx + os[i].match.length).replace(/;.*/, '').match(/\d+/g);
			var ver;
			if (vst) {
				ver = vst[0];
				if (vst.length > 1) ver = ver + '.' + vst[1];
				caps = caps + ',os/' + osn + ver;
			}
			if (os[i].variants) {
				var vrnts = os[i].variants;
				for (var j = 0; j < vrnts.length; j++) {
					if (ua.indexOf(vrnts[j].match, idx) > -1) {
						caps = caps + ',os/' + osn + ver + vrnts[j].value;
						break;
					}
				}
			}
			break;
		}
		var flashVer = 0;
		if (navigator.plugins != null && navigator.plugins.length > 0) {
			if (navigator.plugins["Shockwave Flash 2.0"] || navigator.plugins["Shockwave Flash"]) {
				var swVer2 = navigator.plugins["Shockwave Flash 2.0"] ? " 2.0" : "";
				var fDesc = navigator.plugins["Shockwave Flash" + swVer2].description;
				var dArray = fDesc.split(" ");
				var arrayMajor = dArray[2].split(".");
				var vMajor = arrayMajor[0];
				var vMinor = arrayMajor[1];
				var vRev = dArray[3];
				if (vRev == "") {
					vRev = dArray[4];
				}
				if (vRev[1] == "d") {
					vRev = vRev.substring(1);
				} else if (vRev[0] == "r") {
					vRev = vRev.substring(1);
					if (vRev.indexOf("d") > 0) {
						vRev = vRev.substring(0, vRev.indexOf("d"));
					}
				}
				flashVer = vMajor + "." + vMinor + "." + vRev;
			}
		} else if (typeof window.ActiveXObject != 'undefined') {
			var version;
			var axo;
			var e; /*@cc_on @*/
			/*@if(@_jscript_version >=5)try{axo=new ActiveXObject("ShockwaveFlash.ShockwaveFlash.7");version=axo.GetVariable("$version");tempArray=version.split(" ");version=tempArray[1].split(",").join(".");} catch(e){}
@end @*/
			flashVer = version;
		}
		if (flashVer) {
			verArray = flashVer.split(".");
			var flashMajorVer = verArray[0];
			var flashMinorVer = verArray[1];
			caps = caps + ',swf' + flashMajorVer;
			caps = caps + ',swf' + flashMajorVer + '.' + flashMinorVer;
			var bad_safari = false;
			if (caps.lastIndexOf('ua/safari') > -1) {
				vers = parseInt(caps.substr(caps.lastIndexOf('ua/safari') + 9));
				if (vers >= 6) bad_safari = true;
			}
			if (parseInt(flashMajorVer) >= 10 && !bad_safari) caps = caps + ',swf';
		}
		caps = caps + ',fwv/NrSZIw' + '.' + String.fromCharCode(fwid(0), fwid(1), fwid(2), fwid(3));
		caps = caps + Math.round(ctx._br(100));
		var metas = [{
			name: 'generator',
			match: 'wordpress',
			value: 'cms/wordpress'
		}, {
			name: 'generator',
			match: 'joomla',
			value: 'cms/joomla'
		}, {
			name: 'generator',
			match: 'mediawiki',
			value: 'cms/mediawiki'
		}, {
			name: 'generator',
			match: 'dokuwiki',
			value: 'cms/dokuwiki'
		}, {
			name: 'application-name',
			match: 'phpbb',
			value: 'cms/phpbb'
		}];
		var js_objs = [{
			obj: 'vBulletin',
			value: 'cms/vbulletin'
		}, {
			obj: 'Drupal',
			value: 'cms/drupal'
		}, {
			obj: 'MyBB',
			value: 'cms/mybb'
		}, {
			obj: 'IPBoard',
			value: 'cms/ipb'
		}, {
			obj: 'smf_scripturl',
			value: 'cms/smf'
		}, {
			obj: 'jQuery',
			value: 'jslib/jquery'
		}, {
			obj: 'jQuery.ui',
			value: 'jslib/jqueryui'
		}, {
			obj: 'dojo',
			value: 'jslib/dojo'
		}, {
			obj: 'Prototype',
			value: 'jslib/proto'
		}, {
			obj: 'Scriptaculous',
			value: 'jslib/scriptaculous'
		}, {
			obj: 'Ext',
			value: 'jslib/extjs'
		}, {
			obj: 'YAHOO',
			value: 'jslib/yui'
		}, {
			obj: 'Modernizr',
			value: 'jslib/modernizer'
		}];
		var meta_tags = document.getElementsByTagName('meta');
		for (var i = 0; i < metas.length; i++) {
			for (var j = 0; j < meta_tags.length; j++) {
				if (metas[i].name && metas[i].name == meta_tags[j].name && meta_tags[j].content && meta_tags[j].content.search(new RegExp(metas[i].match, 'i')) > -1) caps += ',' + metas[i].value;
			}
		}
		for (var i = 0; i < js_objs.length; i++) {
			if (!js_objs[i].obj) continue;
			var obj_heir = js_objs[i].obj.split('.');
			var test_obj = 'window';
			var obj_defined = 1;
			for (var j = 0; j < obj_heir.length; j++) {
				test_obj += '.' + obj_heir[j];
				if (eval('typeof(' + test_obj + ')') == 'undefined') {
					obj_defined = 0;
					break;
				}
			}
			if (obj_defined) {
				caps += ',' + js_objs[i].value;
			}
		}
		return caps;
	}
	this._as = function () {
		var i = document.createElement('input');
		i.type = 'text';
		i.name = 'adcopy_response';
		i.setAttribute('autocomplete', 'off');
		i.setAttribute('autocorrect', 'off');
		if (ACPuzzleInfo.theme != 'custom') i.setAttribute('size', 20);
		this._au(i);
		this._aw();
		this.byid('adcopy_response').value = '';
	};
	this._at = function (d) {
		if ('label' in d) this._aw(d.label);
		if ('input' in d) this._av(d.input);
	};
	this._au = function (e) {
		var iid = this._bl('adcopy_response');
		var old = document.getElementById(iid);
		var is_old_ie = false;
		var focus; /*@cc_on @*/
		/*@if(@_jscript_version < 5)is_old_ie=true;@end @*/
		if (!is_old_ie) {
			try {
				focus = (document.activeElement === old);
			} catch (ex) {}
		}
		for (var i = 0; i < old.attributes.length; i++) {
			var attr = old.attributes[i];
			if (!attr.specified) continue;
			if (/^(name|type|auto(complete|correct)|value|size)$/.test(attr.nodeName)) continue;
			e.setAttribute(attr.nodeName, attr.nodeValue);
		}
		if ('tabindex' in ACPuzzleInfo) e.setAttribute('tabindex', ACPuzzleInfo.tabindex);
		old.parentNode.replaceChild(e, old);
		if (focus && typeof e.focus == 'function') e.focus();
		e.id = iid;
	};
	this._av = function (d) {
		if (d.t == 'menu') {
			var opt = [];
			var j;
			var i = document.createElement('select');
			i.name = 'adcopy_response';
			for (j = 0; j < d.v.length / 2; j++) {
				opt.push({
					v: d.v[2 * j],
					t: d.v[2 * j + 1]
				});
			}
			var l = opt.length;
			var e = document.createElement('option');
			e.text = '';
			e.value = '';
			i.options[i.length] = e;
			for (j = 0; j < l; j++) {
				var x;
				if (d.rnd) {
					var r = Math.floor(Math.random() * opt.length);
					x = opt[r];
					opt.splice(r, 1);
				} else {
					x = opt[j];
				}
				var e = document.createElement('option');
				e.value = x.v;
				e.text = x.t;
				i.options[i.length] = e;
			}
			this._au(i);
		}
		if (d.t == 'none') {
			var i = document.createElement('input');
			i.type = 'hidden';
			i.name = 'adcopy_response';
			i.value = '';
			this._au(i);
		}
	};
	this._aw = function (l) {
		var e = this.byid('adcopy-instr');
		if (!e) return;
		if (!l) {
			var lang = this.locale[ACPuzzleInfo.lang] || this.locale.en;
			l = lang.ANSWER;
		}
		e.innerHTML = l;
	};
	this._ax = function () {
		var e = this.byid('adcopy-link-info');
		e.className = ACPuzzleInfo.helpme ? 'adcopy-info-bouncy' : '';
	};
	this._ay = function (tpa) {
		var html = '';
		var i;
		for (i = 0; i < tpa.length; i++) {
			if (tpa[i]) html = html + this._az(tpa[i]);
		}
		if (html) {
			html = this._bw(html);
			html = '<br>' + html;
			var img = this._bb();
			img.innerHTML = html;
			this._ba(img);
		}
	}
	this._az = function (info) {
		var html = '';
		if (!info) return;
		if (info.img) {
			if (typeof (info.img) == 'object') {
				for (var i in info.img) {
					if (info.img.hasOwnProperty(i)) {
						html = html + '<img src="' + info.img[i] + '" alt="" height="1" width="1"/>';
					}
				}
			} else {
				html = html + '<img src="' + info.img + '" alt="" height="1" width="1"/>';
			}
		}
		if (info.js) {
			if (typeof (info.js) == 'object') {
				for (var i in info.js) {
					if (info.js.hasOwnProperty(i)) {
						var j = this._bw(info.js[i]);
						this._bp(j);
					}
				}
			} else {
				var j = this._bw(info.js);
				this._bp(j);
			}
		}
		if (info.html) {
			if (typeof (info.html) == 'object') {
				for (var i in info.html) {
					if (info.html.hasOwnProperty(i)) {
						html = html + info.html[i];
					}
				}
			} else {
				html = html + info.html;
			}
		}
		return html;
	};
	this._ba = function (node) {
		if (node.nodeType != 1) return;
		if (node.tagName.toLowerCase() == 'script') {
			if (node.src) this._bp(node.src);
			if (node.text) eval(node.text);
			return;
		}
		for (var n = node.firstChild; n; n = n.nextSibling) {
			this._ba(n);
		}
	};
	this._bb = function () {
		var img = this.byid('adcopy-pixel-image');
		if (img) return img;
		var id = 'adcopy-pixel-image' + (ACPuzzleInfo.id ? "-" + ACPuzzleInfo.id : '');
		var pi = this.byid('adcopy-puzzle-image');
		img = document.createElement('div');
		img.setAttribute('id', id);
		img.style.display = 'none';
		pi.parentNode.appendChild(img);
		return img;
	};
	this._bc = function (opts) {
		var ph, pv;
		var h = '';
		var k, v;
		var v_type = function (a) {
			if (typeof (a) == 'string' ||
				typeof (a) == 'number') {
				return true;
			}
			return false;
		}
		var h_add = function (a, b) {
			if (!v_type(b)) return;
			if (h.length) h = h + " ";
			h = h + a + ':' + ('' + b).replace(/ /g, '_');
		}
		if (!opts) return '';
		if (!('pagehints' in opts)) return '';
		ph = opts.pagehints;
		if (ph.ver != 1) "abort:incorrect pagehints version" ();
		for (k in ph) {
			if (ph.hasOwnProperty(k)) {
				pv = ph[k];
				if (k == 'ver') continue;
				if (typeof (pv) == 'object') {
					for (v in pv) {
						if (pv.hasOwnProperty(v)) {
							h_add(k, pv[v]);
						}
					}
				} else {
					h_add(k, pv);
				}
			}
		}
		if (h.length > 200) h = h.substr(0, 200);
		return encodeURIComponent(h);
	};
	this._bd = function () {
		var abt_esc = '';
		var abt_dpy = '';
		var abt = function (k, v) {
			var sp = '';
			if (!v) return;
			var l = k.length;
			for (; l < 8; l++) sp = sp + ' ';
			abt_esc = abt_esc + k + ':' + sp + escape(v) + "\n";
			if (typeof (v) == 'string') {
				v = v.replace(/&/g, '&amp;');
				v = v.replace(/</g, '&lt;');
				v = v.replace(/>/g, '&gt;');
			}
			abt_dpy = abt_dpy + k + ':' + sp + v + "\n";
		}
		abt('ckey', ACPuzzleInfo.ckey);
		abt('url', document.location.href);
		abt('theme', ACPuzzleInfo.theme);
		abt('jsid', ACPuzzleInfo.id);
		abt('uid', ACPuzzleInfo.uid);
		abt('ip', ACPuzzleInfo.clientip);
		abt('caps', ACPuzzleInfo.caps);
		abt('ua', navigator.userAgent);
		abt('chid', ACPuzzleInfo.chid);
		abt('time', ACPuzzleInfo.timestamp);
		abt('lang', ACPuzzleInfo.lang);
		abt('type', ACPuzzleInfo.type);
		abt('size', ACPuzzleInfo.size);
		abt('mtyp', ACPuzzleInfo.mediatype);
		abt('murl', ACPuzzleInfo.media_url);
		abt('fail', ACPuzzleInfo.fail);
		var k, s;
		var widgetprops = {
			config: 1,
			pixel: 1,
			player: 1,
			tpdcp: 1
		};
		for (s in widgetprops) {
			if (widgetprops.hasOwnProperty(s) && ACPuzzleInfo.widget[s]) {
				for (k in ACPuzzleInfo.widget[s]) {
					if (ACPuzzleInfo.widget[s].hasOwnProperty(k)) {
						abt('w.' + s + '.' + k, ACPuzzleInfo.widget[s][k]);
					}
				}
			}
		}
		var div = this._be('adcopy-debug-problem');
		var id = this._bl('adcopy-debug-problem');
		var jid = "'" + this._bn() + "'";
		var qid = "'" + id + "'";
		var xid = 'adcopy-unique-' + new Date().getTime();
		var url = this._bu() + '/papi/_log_problem';
		var form = '<hr><b>SEND DETAILS TO SUPPORT?</b><br>' + '<iframe id="' + xid + '" name="' + xid + '" src="about:blank" style="display:none;" onload="ACPuzzle._bg(' + jid + ')"></iframe>' + '<form enctype="multipart/form-data" action="' + url + '" target="' + xid + '" method="POST">' + '<input type="hidden" name="detail" value="' + abt_esc + '">' + '<input type="hidden" name="chid" value="' + ACPuzzleInfo.chid + '">' + 'Please describe the problem<br><textarea name="about" rows=8 cols=45 style="font-size:12px;"></textarea><br>' + 'Do you have anti-virus,firewall,or filtering software? Explain.<br><textarea name="avfwsw" rows=5 cols=45 style="font-size:12px;"></textarea><br>' + '<br>Add data to tech support database,you will not be contacted<br>' + '<input type=submit value="send problem report" onClick="ACPuzzle._bh(' + jid + ')">' + '<button type="button" onClick="ACPuzzle._bf(' + qid + ')">cancel</button></br>' + '</form>';
		ACPuzzleInfo._problem_submitted = 0;
		div.innerHTML = div.innerHTML + '<b>S/M - DIAGNOSTIC REPORT</b>' + '<pre style="white-space:pre-wrap;word-wrap:break-word;">' + abt_dpy + '</pre>' + form;
	};
	this._be = function (popid, mommy, title, initcont) {
		var id = this._bl(popid);
		var div = this.byid(popid);
		var jid = "'" + this._bn() + "'";
		var qpopid = "'" + id + "'";
		var S = function (p, v) {
			div.style[p] = v;
		};
		if (!div) {
			div = document.createElement('div');
			div.setAttribute('id', id);
			if (mommy) {
				mommy.appendChild(div);
			} else {
				document.body.appendChild(div);
				S('position', 'absolute');
				S('top', '100px');
				S('left', '100px');
				S('width', '400px');
			}
			S('zIndex', '10000000');
			S('fontSize', '10px');
			S('border', '1px solid #000');
			S('color', '#000');
			S('backgroundColor', '#FDB');
			S('textAlign', 'left');
			var content = '<span style="float:right;background-color:#fff;border-left:1px solid #000;border-bottom:1px solid #000;' + 'cursor:pointer;" onClick="ACPuzzle._bf(' + qpopid + ')">X</span>';
			if (title) content = content + '<b>' + title + '</b><br>';
			if (initcont) content = content + initcont;
			div.innerHTML = content;
		}
		return div;
	};
	this._bf = function (id) {
		var div = this.byid(id);
		div.parentNode.removeChild(div);
	};
	this._bg = function (id) {
		var that = this._cf(id);
		if (that) return that._bg();
		if (ACPuzzleInfo._problem_submitted) {
			this._bf(this._bl('adcopy-debug-problem'));
		}
	};
	this._bh = function (id) {
		var that = this._cf(id);
		if (that) return that._bh();
		ACPuzzleInfo._problem_submitted = 1;
	};
	this._bi = function (msg) {
		if (opts && opts.keep_serving_broken_puzzles_that_users_cannot_solve__i_know_my_site_is_horribly_misconfigured__i_will_fix_it_before > 1388444998) return;
		var url = this._bu() + '/public/puzzle_diag_help?lang=' + ACPuzzleInfo.lang;
		var mom = this.byid('adcopy-puzzle-image').parentNode;
		var div = this._be('adcopy-debug-output', mom, 'S/M - DIAGNOSTIC LOG', '<div>errors detected - diagnostic mode enabled.<br>for help see:<a target=_sm_diag_help href="' + url + '">help page</a></div>');
		var ndv = document.createElement('div');
		div.appendChild(ndv);
		ndv.innerHTML = msg;
	};
	this._bj = function () {
		var div = this.byid('adcopy-debug-output');
		if (div) {
			div.style.display = '';
			this.byid('adcopy_response').value = '';
		} else {
			this.byid('adcopy_response').value = 'OK';
		}
	}
	this._bk = function () {
		if (ACPuzzleInfo.installation_checked) return;
		ACPuzzleInfo.installation_checked = 1;
		var isbroken;
		var args, key;
		var opts = ACPuzzleInfo.options;
		if (!ACPuzzleInfo.chalapi || !(/script|ajax|overlay|vast|mraid/.test(ACPuzzleInfo.chalapi)) || !ACPuzzleInfo.magic) {
			this._bi('invalid challenge installation:challenge.script or challenge.ajax');
			isbroken = 1;
		}
		if (ACPuzzleInfo.chal_extra_args) {
			args = ACPuzzleInfo.chal_extra_args;
			for (key in args) {
				if (args.hasOwnProperty(key)) {
					this._bi('invalid parameter passed to challenge.' + ACPuzzleInfo.chalapi + ':&nbsp;&nbsp;' + key + '&nbsp;=&gt;' + args[key]);
					isbroken = 1;
				}
			}
		}
		if (!/^[0-9A-Za-z._-]+$/.test(ACPuzzleInfo.ckey)) {
			this._bi('invalid ckey');
			isbroken = 1;
		}
		if (ACPuzzleInfo.theme == 'custom') {
			var reqd = ['adcopy-puzzle-image', 'adcopy-puzzle-audio', 'adcopy-instr', 'adcopy_response', 'adcopy_challenge', 'adcopy-link-refresh', 'adcopy-link-audio', 'adcopy-link-image', 'adcopy-link-info'];
			var i;
			for (i = 0; i < reqd.length; i++) {
				var id = reqd[i];
				if (!this.byid(id)) {
					this._bi('missing required element:' + id);
					isbroken = 1;
				}
			}
		}
		if (isbroken) {
			ACPuzzleInfo.caps = ACPuzzleInfo.caps + ',apibroken';
		}
	};
	this._bl = function (id) {
		return ACPuzzleInfo.id ? id + "-" + ACPuzzleInfo.id : id;
	};
	this._bm = function () {
		return ACPuzzleInfo.id ? '-' + ACPuzzleInfo.id : '';
	};
	this._bn = function () {
		return ACPuzzleInfo.id ? ACPuzzleInfo.id : '';
	};
	this.byid = function (id) {
		var name = this._bl(id);
		return document.getElementById(name);
	};
	this._bo = function (app) {
		var head = document.getElementsByTagName('head');
		var node = (head.length < 1) ? document.body : head[0];
		node.appendChild(app);
	};
	this._bp = function (url) {
		var script = document.createElement('script');
		script.type = 'text/javascript';
		script.src = url;
		this._bo(script);
	};
	this._bq = function () {
		this._bk();
		var i = _ACPuzzleUtil.add_callback(this._bs, this);
		var url = this._bu() + '/papi/_challenge.js' + '?k=' + ACPuzzleInfo.ckey + ';f=' + encodeURIComponent('_ACPuzzleUtil.callbacks[' + i + ']') + ';l=' + ACPuzzleInfo.lang + ';t=' + ACPuzzleInfo.type + ';s=' + ACPuzzleInfo.size + ';c=' + ACPuzzleInfo.caps + ';am=' + ACPuzzleInfo.magic + ';ca=' + ACPuzzleInfo.chalapi + (ACPuzzleInfo.hints ? ';h=' + ACPuzzleInfo.hints : '') + (ACPuzzleInfo.chid ? ';p=' + ACPuzzleInfo.chid : '') + ';ts=1388444998' + ';ct=' + ACPuzzleInfo.chalstamp + (ACPuzzleInfo.mobuid ? ';mu=' + ACPuzzleInfo.mobuid : '') + ';th=' + ACPuzzleInfo.theme + ';r=' + Math.random();
		if (ACPuzzleInfo.demo) {
			if (ACPuzzleInfo.demo.acc) url = url + ';acc=' + ACPuzzleInfo.demo.acc;
			if (ACPuzzleInfo.demo.cmp) url = url + ';cmp=' + ACPuzzleInfo.demo.cmp;
			if (ACPuzzleInfo.demo.crt) url = url + ';crt=' + ACPuzzleInfo.demo.crt;
		}
		if (!ACPuzzleInfo.ckey) {
			this.byid('adcopy-outer').innerHTML = '<b>no ckey specified!</b>';
			return;
		}
		this._bp(url);
	};
	this._br = function (r, x) {
		return Math.random() * r;
	};
	this.reload = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.reload();
		ACPuzzleInfo.error = null;
		ACPuzzleInfo.errormsg = null;
		if (ACPuzzleInfo.stopplaying) ACPuzzleInfo.stopplaying.call(this);
		ACPuzzleInfo.stopplaying = null;
		var context = this;
		setTimeout(function () {
			context._bq.call(context);
		}, 250);
	};
	this._bs = function (obj) {
		if (!obj) obj = {};
		var resp = obj.ACChallengeResult;
		var key;
		ACPuzzleInfo.chid = '';
		ACPuzzleInfo.fail = '';
		for (key in resp) {
			ACPuzzleInfo[key] = resp[key];
		}
		if (!ACPuzzleInfo.chid && !ACPuzzleInfo.fail) {
			ACPuzzleInfo.fail = 'get challenge failed';
		}
		if (ACPuzzleInfo.fail) {
			this.byid('adcopy-outer').innerHTML = '<b>' + ACPuzzleInfo.fail + '</b>';
			return;
		}
		this.byid('adcopy_challenge').value = ACPuzzleInfo.chid;
		var e = this.byid('adcopy-error-msg');
		var i = this.byid('adcopy-instr');
		var l = this.locale[ACPuzzleInfo.lang] || this.locale.en;
		if (e) {
			if (ACPuzzleInfo.error) {
				if (ACPuzzleInfo.errormsg) {
					e.innerHTML = ACPuzzleInfo.errormsg;
				} else {
					e.innerHTML = l.AGAIN;
				}
				e.style.display = 'inline';
				if (i) i.style.display = 'none';
			} else {
				e.innerHTML = '';
				e.style.display = 'none';
				if (i) i.style.display = 'inline';
			}
		}
		ACPuzzleCurrent = this;
		this._ah();
		this._as();
		if (ACPuzzleInfo.widget.config) this._at(ACPuzzleInfo.widget.config);
		this._ax();
		this._ay([ACPuzzleInfo.widget.pixel, ACPuzzleInfo.widget.tpdcp]);
		this._ai();
		if (ACPuzzleInfo.callback) ACPuzzleInfo.callback.call(this);
		ACPuzzleInfo.callback = null;
		ACPuzzleCurrent = null;
	};
	this.media_url = function () {
		if (ACPuzzleInfo.media_url) return ACPuzzleInfo.media_url;
		var thm = this._ca();
		var width = this.size[ACPuzzleInfo.size].w;
		var height = this.size[ACPuzzleInfo.size].h;
		var url = this._bv() + '/papi/media?c=' + ACPuzzleInfo.chid + ';w=' + width + ';h=' + height;
		var img = this.byid('adcopy-puzzle-image');
		if (thm && ('fg' in thm) && ('bg' in thm)) {
			url = url + ';fg=' + this._bz(thm.fg);
			url = url + ';bg=' + this._bz(thm.bg);
		} else {
			var fg, bg, vfg, vbg;
			var e = img;
			while (e) {
				if (!fg) {
					vfg = this._bx(e, 'color', 'color');
					if (this._by(vfg)) fg = vfg;
				}
				if (!bg) {
					vbg = this._bx(e, 'background-color', 'backgroundColor');
					if (this._by(vbg)) bg = vbg;
				}
				if (fg && bg) break;
				if (e.nodeName == 'BODY') break;
				e = e.parentNode;
			}
			if (fg) url = url + ';fg=' + this._bz(fg);
			if (bg) url = url + ';bg=' + this._bz(bg);
		}
		return url;
	};
	this._bt = function (forcesec) {
		var url = ACPuzzleInfo.apiserver + '/papi/action?c=' + ACPuzzleInfo.chid;
		if (forcesec) url = url.replace(/api\./, 'api-secure.');
		url = ((url.match(/-secure/) || forcesec) ? 'https:' : 'http:') + url;
		return url;
	};
	this._bu = function () {
		return (ACPuzzleInfo.protocol || '') + ACPuzzleInfo.apiserver;
	};
	this._bv = function () {
		return (ACPuzzleInfo.protocol || '') + ACPuzzleInfo.mediaserver;
	};
	this._bw = function (url) {
		if (!url) return url;
		url = url.replace(/{ac:actionurl}/g, this._bt(0));
		url = url.replace(/{ac:actionsecurl}/g, this._bt(1));
		url = url.replace(/{ac:chid}/g, ACPuzzleInfo.chid);
		url = url.replace(/{ac:userid}/g, ACPuzzleInfo.uid);
		url = url.replace(/{ac:bestuid}/g, ACPuzzleInfo.bestuid);
		url = url.replace(/{ac:timestamp}/g, new Date().getTime());
		return url;
	};
	this._bx = function (e, p1, p2) {
		var v;
		if (!e) return;
		if ((document.defaultView) && (document.defaultView.getComputedStyle)) {
			v = document.defaultView.getComputedStyle(e, null)[p1];
			if (v) return v;
			v = document.defaultView.getComputedStyle(e, null)[p2];
			if (v) return v;
			v = document.defaultView.getComputedStyle(e, null).getPropertyValue(p1);
			if (v) return v;
			v = document.defaultView.getComputedStyle(e, null).getPropertyValue(p2);
			if (v) return v;
		} else if (e.currentStyle) {
			if (e.currentStyle[p1]) return e.currentStyle[p1];
			if (e.currentStyle[p2]) return e.currentStyle[p2];
		}
	};
	this._by = function (c) {
		if (!c) return null;
		if (/rgba.*,?0\)/.test(c)) return null;
		if (/transparent/.test(c)) return null;
		return 1;
	};
	this._bz = function (x) {
		var c = x.replace(/#/, '');
		if (/^rgb/.test(c)) {
			c = c.replace(/^.*\(/, '');
			c = c.replace(/[\(\)]/g, '');
			var a = c.split(',');
			for (var n in [0, 1, 2]) {
				a[n] = parseInt(a[n]);
				a[n] = a[n].toString(16);
				if (a[n].length == 1) a[n] = '0' + a[n];
			}
			return a[0] + a[1] + a[2];
		}
		if (c.length == 6) return c;
		if (c.length == 3) {
			var a = c.split('');
			return a[0] + a[0] + a[1] + a[1] + a[2] + a[2];
		}
		return null;
	};
	this.change_type = function (t, puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.change_type(t);
		ACPuzzleInfo.type = t;
		this.reload();
	};
	this.moreinfo = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.moreinfo();
		var ans = this.get_response();
		if (ans == 'XYZZY') {
			this._bd();
			return;
		}
		if (ans == 'TEST MODE ACTIVATE') {
			this._bj();
			return;
		}
		if (typeof (this.win) == 'undefined' || this.win.closed) {
			var url = this._bu() + '/public/puzzle_more_info?lang=' + ACPuzzleInfo.lang + ';chid=' + ACPuzzleInfo.chid;
			this.win = window.open(url, 'POPUP', "toolbar=no,status=no,location=no,menubar=no," + "resizable=yes,scrollbars=yes,height=660,width=650", 'yes');
			this.win.focus();
		} else {
			this.win.focus();
		}
	};
	this.change2audio = function (puzzle_id) {
		this.change_type('aud', puzzle_id);
	};
	this.change2image = function (puzzle_id) {
		this.change_type('img', puzzle_id);
	};
	this._ca = function () {
		if (typeof (ACPuzzleInfo.theme) == 'object') return ACPuzzleInfo.theme;
		return this.theme[ACPuzzleInfo.theme];
	};
	this._cb = function () {
		var width = this.size[ACPuzzleInfo.size].w;
		var height = this.size[ACPuzzleInfo.size].h;
		var media = this._bv() + '/media';
		var thm = this._ca();
		var css = this.css;
		var id = this._bm();
		if (ACPuzzleInfo.theme == 'none') return;
		css = css.replace(/_ID_/g, id);
		css = css.replace(/_WIDTH_/g, width);
		css = css.replace(/_WIDTHP1_/g, width + 1);
		css = css.replace(/_WIDTHM115_/g, width - 115);
		css = css.replace(/_WIDTHM190_/g, width - 190);
		css = css.replace(/_HEIGHT_/g, height);
		css = css.replace(/_MEDIA_/g, media);
		css = css.replace(/_BGCOLOR_/g, thm.bg);
		css = css.replace(/_BDCOLOR_/g, thm.bd);
		css = css.replace(/_FGCOLOR_/g, thm.fg);
		css = css.replace(/_LKCOLOR_/g, thm.lk);
		css = css.replace(/_HVCOLOR_/g, thm.hv);
		css = css.replace(/_ERCOLOR_/g, thm.er);
		css = css.replace(/_SUFFIX_/g, (thm.is || '-bk'));
		return css;
	};
	this._cc = function (css) {
		var styleElement = document.createElement("style");
		styleElement.type = "text/css";
		if (styleElement.styleSheet) {
			styleElement.styleSheet.cssText = css;
		} else {
			styleElement.appendChild(document.createTextNode(css));
		}
		this._bo(styleElement);
	};
	this._cd = function () {
		var html = unescape(this.html);
		var media = this._bv() + '/media';
		var lang = this.locale[ACPuzzleInfo.lang] || this.locale.en;
		var thm = this._ca();
		var id = this._bm();
		var jsid = this._bn();
		html = html.replace(/_ID_/g, id);
		html = html.replace(/_JSID_/g, jsid);
		html = html.replace(/_SUFFIX_/g, (thm.is || '-bk'));
		html = html.replace(/_LOGOSUFFIX_/g, (thm.ls || '-bk'));
		html = html.replace(/_MEDIA_/g, media);
		html = html.replace(/_ANSWER_/g, lang.ANSWER);
		html = html.replace(/_NEWPUZ_/g, lang.NEWPUZ);
		html = html.replace(/_AUDIO_/g, lang.AUDIO);
		html = html.replace(/_VISUAL_/g, lang.VISUAL);
		html = html.replace(/_INFO_/g, lang.INFO);
		return html;
	};
	this._ce = function (opts) {
		ACPuzzleInfo.caps = this._ar();
		ACPuzzleInfo.hints = this._bc(opts);
		if (!opts) return;
		if (opts.lang == 'jp') opts.lang = 'ja';
		if (opts.lang == 'nb') opts.lang = 'no';
		if (opts.lang in this.locale) {
			ACPuzzleInfo.lang = opts.lang;
		}
		if (opts.size in this.size) {
			ACPuzzleInfo.size = opts.size;
		}
		if ((opts.theme in this.theme) || (typeof (opts.theme) == 'object')) {
			ACPuzzleInfo.theme = opts.theme;
		}
		if (opts.tabindex) {
			ACPuzzleInfo.tabindex = opts.tabindex;
		}
		ACPuzzleInfo.demo = opts.demo;
		ACPuzzleInfo.callback = opts.callback;
		ACPuzzleInfo.onerror = opts.onerror;
		ACPuzzleInfo.id = opts.id;
		ACPuzzleInfo.options = opts;
	};
	this.script_init = function () {
		this._ce(ACPuzzleOptions);
		if (ACPuzzleInfo.theme != 'custom') {
			if (this.byid('adcopy_response')) {
				return;
			}
			document.write('<style type="text/css">' + this._cb() + '</style>');
			document.write(this._cd());
			this._bq();
		} else {
			if (document.getElementById('adcopy_challenge')) {
				this._bq();
			} else {
				var f = window.onload;
				var me = this;
				window.onload = function () {
					me._bq();
					if (f) f();
				};
			}
		}
	};
	this._cf = function (puzzle_id) {
		var puz;
		if (ACPuzzleInfo.multi && puzzle_id && ACPuzzleInfo.id != puzzle_id) {
			puz = _ACPuzzleUtil.get_puzzle(puzzle_id);
		}
		return puz;
	};
	this.create = function (ckey, divid, opts) {
		if (opts && opts.multi) {
			if (ACPuzzleInfo.multi === false) {
				return;
			}
			ACPuzzleInfo.multi = true;
			var id = opts.id;
			if (!id) {
				id = divid;
				opts.id = id;
			}
			var that = this._cf(id);
			if (that) {
				return that.create(ckey, divid, opts);
			}
			if (this === ACPuzzle) {
				var thisinfo = ACPuzzle.PuzzleInfo();
				var newinfo = {};
				for (var key in thisinfo) {
					newinfo[key] = thisinfo[key];
				}
				var puz = new ACPuzzleObject(newinfo);
				return puz.create(ckey, divid, opts);
			} else {
				_ACPuzzleUtil.add_puzzle(this, id);
			}
		} else if (ACPuzzleInfo) {
			if (ACPuzzleInfo.multi) {
				return;
			} else {
				ACPuzzleInfo.multi = false;
			}
		}
		if (typeof ACPuzzleInfo == 'undefined') ACPuzzleInfo = opts;
		this._ce(opts);
		ACPuzzleInfo.ckey = ckey;
		if (ACPuzzleInfo.theme == 'custom') {
			this.reload();
		} else {
			var div = document.getElementById(divid);
			if (!ACPuzzleInfo.cssp) {
				this._cc(this._cb());
				ACPuzzleInfo.cssp = 1;
			}
			if (div) {
				this.destroy();
				ACPuzzleInfo.divid = divid;
				div.innerHTML = this._cd();
				this.reload();
			}
		}
		return this;
	};
	this.destroy = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.destroy();
		if (typeof ACPuzzleInfo.divid != 'undefined') {
			var div = document.getElementById(ACPuzzleInfo.divid);
			if (div) div.innerHTML = '';
		}
	};
	this.switch_type = function (t, puzzle_id) {
		if (t == 'audio') {
			change_type('aud', puzzle_id);
		} else {
			change_type('img', puzzle_id);
		}
	};
	this.show_help = function (puzzle_id) {
		this.moreinfo(puzzle_id);
	};
	this.get_challenge = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.get_challenge();
		return ACPuzzleInfo.chid;
	};
	this.get_userid = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.get_userid();
		return ACPuzzleInfo.uid;
	};
	this.get_response = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.get_response();
		return this.byid('adcopy_response').value;
	};
	this.focus_response_field = function (puzzle_id) {
		var that = this._cf(puzzle_id);
		if (that) return that.focus_response_field();
		this.byid('adcopy_response').focus();
	};
};
if (typeof ACPuzzleInfo == 'object') {
	if (typeof ACPuzzle == 'undefined') ACPuzzle = new ACPuzzleObject(ACPuzzleInfo);
	if (ACPuzzleInfo.onload) {
		ACPuzzleInfo.onload();
		ACPuzzleInfo.onload = null;
	}
} 