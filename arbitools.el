;Copyright 2014 David González Gándara
;This program is free software: you can redistribute it and/or modify
;    it under the terms of the GNU General Public License as published by
;    the Free Software Foundation, either version 3 of the License, or
;    (at your option) any later version.
;
;    This program is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License for more details.
;
;    You should have received a copy of the GNU General Public License
;    along with this program.  If not, see <http://www.gnu.org/licenses/>.


(defun arbitools-update (list method)
  (interactive "slist: \nsmethod:")
  (shell-command (concat (expand-file-name "arbitools-update.py") " -l " list " -m " method " -i " buffer-file-name)))

(defun arbitools-add (addfile)
  (interactive "saddfile: ")
  (shell-command (concat (expand-file-mame "arbitools-add.py") " -a " addfile " -i " buffer-file-name)))

(defun arbitools-standings ()
  (interactive)
  (shell-command (concat (expand-file-name "arbitools-standings.py") " -i " buffer-file-name)))



(defvar arbitools-mode-hook nil)

(defvar arbitools-mode-map
  (let ((map (make-keymap)))
    (define key-map "\C-j" 'newline-and-indent)
    map)
   "keymap for arbitools mode")

(add-to-list 'auto-mode-alist '("\\.veg\\'" . arbitools-mode))

(defconst arbitools-font-lock-keywords-1
  (list
    `(,(regexp-opt '("NAME" "COUNTRY" "BIRTHDAY" "TITLE" "ELOFIDE" "IDEFIDE") t) . font-lock-keyword-face)
    '("\\('\\w*'\\)" . font-lock-variable-name-face))
   "Expresions for arbitools mode")

(defvar arbitools-mode-syntax-table
  (let ((st (make-syntax-table)))

  (modify syntax-entry ?_ "w" st)
  st)
  "Syntax table for arbitools-mode")

(defun arbitools-mode()
  "Major mode for Chess Tournament management"
  (interactive)
  (kill-all-local-variables)
  (use-local-map arbitools-mode-map)

  (set (make-local-variable 'font-lock-defaults) '(arbitools-font-lock-keywords-1))

  (setq major-mode 'arbitools-mode)
  (setq mode-name "arbitools")
  (run-hooks 'arbitools-mode-hook))

(provide 'arbitools-mode)

