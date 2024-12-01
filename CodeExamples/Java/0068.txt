/*
 * Copyright 2015 Namihiko Matsumura (https://github.com/n-i-e/)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.github.n_i_e.deepfolderview;

import java.awt.Toolkit;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.StringSelection;
import java.io.IOException;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.PojoProperties;
import org.eclipse.core.databinding.observable.Realm;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.jface.databinding.swt.SWTObservables;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.wb.swt.SWTResourceManager;

import com.github.n_i_e.dirtreedb.Assertion;
import com.github.n_i_e.dirtreedb.DBPathEntry;
import com.github.n_i_e.dirtreedb.PathEntry;
import com.github.n_i_e.dirtreedb.lazy.LazyRunnable;
import com.github.n_i_e.dirtreedb.lazy.LazyUpdater;
import com.github.n_i_e.dirtreedb.lazy.LazyUpdater.Dispatcher;
import com.ibm.icu.text.NumberFormat;
import com.ibm.icu.text.SimpleDateFormat;

public class SwtFileFolderMenu extends SwtCommonFileFolderMenu {
	@SuppressWarnings("unused")
	private DataBindingContext m_bindingContext;

	protected Shell shell;
	private FormToolkit formToolkit = new FormToolkit(Display.getDefault());
	private Text txtLocation;
	private Composite compositeToolBar;
	private Table table;
	private Label lblStatusBar;
	private Composite compositeStatusBar;
	private ProgressBar progressBar;

	@Override protected Shell getShell() { return shell; }
	@Override protected Table getTable() { return table; }
	@Override protected Label getLblStatusBar() { return lblStatusBar; }
	@Override protected ProgressBar getProgressBar() { return progressBar; }

 	public static void main(String[] args) {
		final Display display = Display.getDefault();

		Realm.runWithDefault(SWTObservables.getRealm(display), new Runnable() {
			public void run() {
				try {
					final SwtFileFolderMenu window = new SwtFileFolderMenu();
					window.open();
/*
					display.asyncExec(new Runnable() {
						public void run() {
							TableItem tableItem = new TableItem(window.table, SWT.NONE);
							tableItem.setText(new String[] {"C:\\", "2015-01-01 00:00:00", "1", "2", "3"});

							TableItem tableItem_1 = new TableItem(window.table, SWT.NONE);
							tableItem_1.setText(new String[] {"D:\\", "2014-01-01 00:00:00", "100", "200", "1"});
						}
					});*/
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	public void open() {
		Display display = Display.getDefault();
		//createContents();
		//shell.open();
		//shell.layout();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) {
				display.sleep();
			}
		}
	}


	public SwtFileFolderMenu() {
		createContents();
		shell.open();
		shell.layout();

		location = new NavigatableList<Location>();
		location.add(new Location());
	}

	/**
	 * Create contents of the window.
	 */
	private void createContents() {
		shell = new Shell();
		shell.addDisposeListener(new DisposeListener() {
			public void widgetDisposed(DisposeEvent arg0) {
				Point p = shell.getSize();
				PreferenceRW.setSwtFileFolderMenuWindowWidth(p.x);
				PreferenceRW.setSwtFileFolderMenuWindowHeight(p.y);
			}
		});
		shell.setImage(SWTResourceManager.getImage(SwtFileFolderMenu.class, "/com/github/n_i_e/deepfolderview/icon/drive-harddisk.png"));
		shell.setMinimumSize(new Point(300, 200));
		shell.setSize(PreferenceRW.getSwtFileFolderMenuWindowWidth(), PreferenceRW.getSwtFileFolderMenuWindowHeight());
		GridLayout gl_shell = new GridLayout(1, false);
		gl_shell.verticalSpacing = 6;
		gl_shell.marginWidth = 3;
		gl_shell.marginHeight = 3;
		gl_shell.horizontalSpacing = 6;
		shell.setLayout(gl_shell);

		Menu menu = new Menu(shell, SWT.BAR);
		shell.setMenuBar(menu);

		MenuItem mntmFile = new MenuItem(menu, SWT.CASCADE);
		mntmFile.setText(Messages.mntmFile_text);

		Menu menuFile = new Menu(mntmFile);
		mntmFile.setMenu(menuFile);

		MenuItem mntmOpen_1 = new MenuItem(menuFile, SWT.NONE);
		mntmOpen_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onOpenSelected(e);
			}
		});
		mntmOpen_1.setText(Messages.mntmOpen_text);

		MenuItem mntmOpenInNew_1 = new MenuItem(menuFile, SWT.NONE);
		mntmOpenInNew_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onOpenInNewWindowSelected(e);
			}
		});
		mntmOpenInNew_1.setText(Messages.mntmOpenInNewWindow_text);

		MenuItem mntmOpenDuplicateDetails_1 = new MenuItem(menuFile, SWT.NONE);
		mntmOpenDuplicateDetails_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onOpenDuplicateDetailsSelected(e);
			}
		});
		mntmOpenDuplicateDetails_1.setText(Messages.mntmOpenDuplicateDetails_text);

		MenuItem mntmCopyTo_2 = new MenuItem(menuFile, SWT.NONE);
		mntmCopyTo_2.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onCopyToSelected();
			}
		});
		mntmCopyTo_2.setText(Messages.mntmCopyTo_text);

		MenuItem mntmClose = new MenuItem(menuFile, SWT.NONE);
		mntmClose.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onCloseSelected();
			}
		});
		mntmClose.setText(Messages.mntmClose_text);

		MenuItem mntmQuit = new MenuItem(menuFile, SWT.NONE);
		mntmQuit.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onQuitSelected();
			}
		});
		mntmQuit.setText(Messages.mntmQuit_text);

		MenuItem mntmEdit = new MenuItem(menu, SWT.CASCADE);
		mntmEdit.setText(Messages.mntmEdit_text);

		Menu menuEdit = new Menu(mntmEdit);
		mntmEdit.setMenu(menuEdit);

		MenuItem mntmRun_1 = new MenuItem(menuEdit, SWT.NONE);
		mntmRun_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onRunSelected();
			}
		});
		mntmRun_1.setText(Messages.mntmRun_text);

		MenuItem mntmCopyAsString_1 = new MenuItem(menuEdit, SWT.NONE);
		mntmCopyAsString_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onCopyAsStringSelected();
			}
		});
		mntmCopyAsString_1.setText(Messages.mntmCopyAsString_text);

		MenuItem mntmCopyTo_1 = new MenuItem(menuEdit, SWT.NONE);
		mntmCopyTo_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onCopyToSelected();
			}
		});
		mntmCopyTo_1.setText(Messages.mntmCopyTo_text);

		MenuItem mntmVisibility = new MenuItem(menu, SWT.CASCADE);
		mntmVisibility.setText(Messages.mntmVisibility_text);

		Menu menuVisibility = new Menu(mntmVisibility);
		mntmVisibility.setMenu(menuVisibility);

		final MenuItem mntmFoldersVisible = new MenuItem(menuVisibility, SWT.CHECK);
		mntmFoldersVisible.setSelection(true);
		mntmFoldersVisible.setText(Messages.mntmFoldersVisible_text);

		final MenuItem mntmFilesVisible = new MenuItem(menuVisibility, SWT.CHECK);
		mntmFilesVisible.setSelection(true);
		mntmFilesVisible.setText(Messages.mntmFilesVisible_text);

		final MenuItem mntmCompressedFoldersVisible = new MenuItem(menuVisibility, SWT.CHECK);
		mntmCompressedFoldersVisible.setSelection(true);
		mntmCompressedFoldersVisible.setText(Messages.mntmCompressedFoldersVisible_text);

		final MenuItem mntmCompressedFilesVisible = new MenuItem(menuVisibility, SWT.CHECK);
		mntmCompressedFilesVisible.setSelection(true);
		mntmCompressedFilesVisible.setText(Messages.mntmCompressedFilesVisible_text);

		MenuItem mntmHelp = new MenuItem(menu, SWT.CASCADE);
		mntmHelp.setText(Messages.mntmHelp_text);

		Menu menuHelp = new Menu(mntmHelp);
		mntmHelp.setMenu(menuHelp);

		MenuItem mntmOpenSourceLicenses = new MenuItem(menuHelp, SWT.NONE);
		mntmOpenSourceLicenses.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				new SwtOpenSourceLicenses(shell, SWT.TITLE|SWT.MIN|SWT.MAX|SWT.CLOSE).open();
			}
		});
		mntmOpenSourceLicenses.setText(Messages.mntmOpenSourceLicenses_text);

		compositeToolBar = new Composite(shell, SWT.NONE);
		compositeToolBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		compositeToolBar.setBackground(SWTResourceManager.getColor(SWT.COLOR_WIDGET_BACKGROUND));
		compositeToolBar.setFont(SWTResourceManager.getFont("Meiryo UI", 12, SWT.NORMAL));
		GridLayout gl_compositeToolBar = new GridLayout(5, false);
		gl_compositeToolBar.horizontalSpacing = 0;
		gl_compositeToolBar.verticalSpacing = 0;
		gl_compositeToolBar.marginWidth = 0;
		gl_compositeToolBar.marginHeight = 0;
		compositeToolBar.setLayout(gl_compositeToolBar);
		formToolkit.adapt(compositeToolBar);
		formToolkit.paintBordersFor(compositeToolBar);

		Button btnLeft = new Button(compositeToolBar, SWT.NONE);
		btnLeft.setImage(SWTResourceManager.getImage(SwtFileFolderMenu.class, "/com/github/n_i_e/deepfolderview/icon/go-previous.png"));
		btnLeft.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onNavigatePreviousSelected(e);
			}
		});
		btnLeft.setFont(SWTResourceManager.getFont("Meiryo UI", 11, SWT.NORMAL));
		formToolkit.adapt(btnLeft, true, true);

		Button btnRight = new Button(compositeToolBar, SWT.NONE);
		btnRight.setImage(SWTResourceManager.getImage(SwtFileFolderMenu.class, "/com/github/n_i_e/deepfolderview/icon/go-next.png"));
		btnRight.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onNavigateNextSelected(e);
			}
		});
		btnRight.setFont(SWTResourceManager.getFont("Meiryo UI", 11, SWT.NORMAL));
		formToolkit.adapt(btnRight, true, true);

		Button btnUp = new Button(compositeToolBar, SWT.NONE);
		btnUp.setImage(SWTResourceManager.getImage(SwtFileFolderMenu.class, "/com/github/n_i_e/deepfolderview/icon/go-up.png"));
		btnUp.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onUpperFolderSelected(e);
			}
		});
		formToolkit.adapt(btnUp, true, true);

		txtLocation = new Text(compositeToolBar, SWT.BORDER);
		txtLocation.addModifyListener(new ModifyListener() {
			public void modifyText(ModifyEvent arg0) {
				onLocationModified(arg0);
			}
		});
		GridData gd_txtLocation = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		gd_txtLocation.widthHint = 200;
		txtLocation.setLayoutData(gd_txtLocation);
		txtLocation.setFont(SWTResourceManager.getFont("Meiryo UI", 11, SWT.NORMAL));
		formToolkit.adapt(txtLocation, true, true);

		Button btnRefresh = new Button(compositeToolBar, SWT.NONE);
		btnRefresh.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				refresh();
			}
		});
		btnRefresh.setImage(SWTResourceManager.getImage(SwtFileFolderMenu.class, "/com/github/n_i_e/deepfolderview/icon/view-refresh.png"));
		formToolkit.adapt(btnRefresh, true, true);

		final TableViewer tableViewer = new TableViewer(shell, SWT.MULTI | SWT.BORDER | SWT.FULL_SELECTION | SWT.VIRTUAL);
		table = tableViewer.getTable();
		table.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 1, 1));
		//table = new Table(scrolledComposite, SWT.BORDER | SWT.FULL_SELECTION | SWT.VIRTUAL);
		table.setHeaderVisible(true);
		table.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onTableSelected(e);
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				onOpenSelected(e);
			}
		});
		formToolkit.adapt(table);
		formToolkit.paintBordersFor(table);

		final TableColumn tblclmnPath = new TableColumn(table, SWT.LEFT);
		tblclmnPath.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				table.setSortColumn(tblclmnPath);
				if (table.getSortDirection() == SWT.UP) {
					table.setSortDirection(SWT.DOWN);
				} else {
					table.setSortDirection(SWT.UP);
				}
				onTblclmnPathSelected(tblclmnPath, e);
			}
		});
		tblclmnPath.setWidth(230);
		tblclmnPath.setText(Messages.tblclmnPath_text);
		setTableSortDirection(tblclmnPath, "path", order);

		final TableColumn tblclmnDateLastModified = new TableColumn(table, SWT.LEFT);
		tblclmnDateLastModified.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				table.setSortColumn(tblclmnDateLastModified);
				if (table.getSortDirection() == SWT.UP) {
					table.setSortDirection(SWT.DOWN);
				} else {
					table.setSortDirection(SWT.UP);
				}
				onTblclmnDateLastModifiedSelected(tblclmnDateLastModified, e);
			}
		});
		tblclmnDateLastModified.setWidth(136);
		tblclmnDateLastModified.setText(Messages.tblclmnDateLastModified_text);
		setTableSortDirection(tblclmnDateLastModified, "datelastmodified", order);

		final TableColumn tblclmnSize = new TableColumn(table, SWT.RIGHT);
		tblclmnSize.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				table.setSortColumn(tblclmnSize);
				if (table.getSortDirection() == SWT.UP) {
					table.setSortDirection(SWT.DOWN);
				} else {
					table.setSortDirection(SWT.UP);
				}
				onTblclmnSizeSelected(tblclmnSize, e);
			}
		});
		tblclmnSize.setWidth(110);
		tblclmnSize.setText(Messages.tblclmnSize_text);
		setTableSortDirection(tblclmnSize, "size", order);

		final TableColumn tblclmnCompressedsize = new TableColumn(table, SWT.RIGHT);
		tblclmnCompressedsize.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				table.setSortColumn(tblclmnCompressedsize);
				if (table.getSortDirection() == SWT.UP) {
					table.setSortDirection(SWT.DOWN);
				} else {
					table.setSortDirection(SWT.UP);
				}
				onTblclmnCompressedsizeSelected(tblclmnCompressedsize, e);
			}
		});
		tblclmnCompressedsize.setWidth(110);
		tblclmnCompressedsize.setText(Messages.tblclmnCompressedesize_text);
		setTableSortDirection(tblclmnCompressedsize, "compressedsize", order);

		final TableColumn tblclmnDuplicate = new TableColumn(table, SWT.NONE);
		tblclmnDuplicate.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				table.setSortColumn(tblclmnDuplicate);
				if (table.getSortDirection() == SWT.UP) {
					table.setSortDirection(SWT.DOWN);
				} else {
					table.setSortDirection(SWT.UP);
				}
				onTblclmnDuplicateSelected(tblclmnDuplicate, e);
			}
		});
		tblclmnDuplicate.setWidth(35);
		tblclmnDuplicate.setText(Messages.tblclmnDuplicate_text);
		setTableSortDirection(tblclmnDuplicate, "duplicate", order);

		final TableColumn tblclmnDedupablesize = new TableColumn(table, SWT.RIGHT);
		tblclmnDedupablesize.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				table.setSortColumn(tblclmnDedupablesize);
				if (table.getSortDirection() == SWT.UP) {
					table.setSortDirection(SWT.DOWN);
				} else {
					table.setSortDirection(SWT.UP);
				}
				onTblclmnDedupablesizeSelected(tblclmnDedupablesize, e);
			}
		});
		tblclmnDedupablesize.setWidth(110);
		tblclmnDedupablesize.setText(Messages.tblclmnDedupablesize_text);
		setTableSortDirection(tblclmnDedupablesize, "dedupablesize", order);

		Menu popupMenu = new Menu(table);
		table.setMenu(popupMenu);

		MenuItem mntmRun = new MenuItem(popupMenu, SWT.NONE);
		mntmRun.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onRunSelected();
			}
		});
		mntmRun.setText(Messages.mntmRun_text);

		MenuItem mntmOpen = new MenuItem(popupMenu, SWT.NONE);
		mntmOpen.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onOpenSelected(e);
			}
		});
		mntmOpen.setText(Messages.mntmOpen_text);

		MenuItem mntmOpenInNew = new MenuItem(popupMenu, SWT.NONE);
		mntmOpenInNew.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onOpenInNewWindowSelected(e);
			}
		});
		mntmOpenInNew.setText(Messages.mntmOpenInNewWindow_text);

		MenuItem mntmOpenDuplicateDetails = new MenuItem(popupMenu, SWT.NONE);
		mntmOpenDuplicateDetails.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onOpenDuplicateDetailsSelected(e);
			}
		});
		mntmOpenDuplicateDetails.setText(Messages.mntmOpenDuplicateDetails_text);

		MenuItem mntmCopyAsString = new MenuItem(popupMenu, SWT.NONE);
		mntmCopyAsString.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onCopyAsStringSelected();
			}
		});
		mntmCopyAsString.setText(Messages.mntmCopyAsString_text);

		MenuItem mntmCopyTo = new MenuItem(popupMenu, SWT.NONE);
		mntmCopyTo.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				onCopyToSelected();
			}
		});
		mntmCopyTo.setText(Messages.mntmCopyTo_text);

		MenuItem menuItem = new MenuItem(popupMenu, SWT.SEPARATOR);
		menuItem.setText("Visibility");

		final MenuItem mntmFoldersVisible_1 = new MenuItem(popupMenu, SWT.CHECK);
		mntmFoldersVisible_1.setSelection(true);
		mntmFoldersVisible_1.setText(Messages.mntmFoldersVisible_text);
		mntmFoldersVisible_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				mntmFoldersVisible.setSelection(mntmFoldersVisible_1.getSelection());
				onFoldersVisibleChecked(mntmFoldersVisible.getSelection());
			}
		});

		final MenuItem mntmFilesVisible_1 = new MenuItem(popupMenu, SWT.CHECK);
		mntmFilesVisible_1.setSelection(true);
		mntmFilesVisible_1.setText(Messages.mntmFilesVisible_text);
		mntmFilesVisible_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				mntmFilesVisible.setSelection(mntmFilesVisible_1.getSelection());
				onFilesVisibleChecked(mntmFilesVisible.getSelection());
			}
		});

		final MenuItem mntmCompressedFoldersVisible_1 = new MenuItem(popupMenu, SWT.CHECK);
		mntmCompressedFoldersVisible_1.setSelection(true);
		mntmCompressedFoldersVisible_1.setText(Messages.mntmCompressedFoldersVisible_text);
		mntmCompressedFoldersVisible_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				mntmCompressedFoldersVisible.setSelection(mntmCompressedFoldersVisible_1.getSelection());
				onCompressedFoldersVisibleChecked(mntmCompressedFoldersVisible.getSelection());
			}
		});

		final MenuItem mntmCompressedFilesVisible_1 = new MenuItem(popupMenu, SWT.CHECK);
		mntmCompressedFilesVisible_1.setSelection(true);
		mntmCompressedFilesVisible_1.setText(Messages.mntmCompressedFilesVisible_text);
		mntmCompressedFilesVisible_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				mntmCompressedFilesVisible.setSelection(mntmCompressedFilesVisible_1.getSelection());
				onCompressedFilesVisibleSelected(mntmCompressedFilesVisible.getSelection());
			}
		});
		mntmFoldersVisible.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				mntmFoldersVisible_1.setSelection(mntmFoldersVisible.getSelection());
				onFoldersVisibleChecked(mntmFoldersVisible.getSelection());
			}
		});
		mntmFilesVisible.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
			    mntmFilesVisible_1.setSelection(mntmFilesVisible.getSelection());
				onFilesVisibleChecked(mntmFilesVisible.getSelection());
			}
		});
		mntmCompressedFoldersVisible.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
			    mntmCompressedFoldersVisible_1.setSelection(mntmCompressedFoldersVisible.getSelection());
				onCompressedFoldersVisibleChecked(mntmCompressedFoldersVisible.getSelection());
			}
		});
		mntmCompressedFilesVisible.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
			    mntmCompressedFilesVisible_1.setSelection(mntmCompressedFilesVisible.getSelection());
				onCompressedFilesVisibleSelected(mntmCompressedFilesVisible.getSelection());
			}
		});

		compositeStatusBar = new Composite(shell, SWT.NONE);
		compositeStatusBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		compositeStatusBar.setBackground(SWTResourceManager.getColor(SWT.COLOR_WIDGET_BACKGROUND));
		GridLayout gl_compositeStatusBar = new GridLayout(2, false);
		gl_compositeStatusBar.marginWidth = 0;
		gl_compositeStatusBar.marginHeight = 0;
		compositeStatusBar.setLayout(gl_compositeStatusBar);
		formToolkit.adapt(compositeStatusBar);
		formToolkit.paintBordersFor(compositeStatusBar);

		lblStatusBar = new Label(compositeStatusBar, SWT.NONE);
		lblStatusBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		lblStatusBar.setBackground(SWTResourceManager.getColor(SWT.COLOR_WIDGET_BACKGROUND));
		formToolkit.adapt(lblStatusBar, true, true);
		lblStatusBar.setText("");

		progressBar = new ProgressBar(compositeStatusBar, SWT.NONE);
		formToolkit.adapt(progressBar, true, true);
		m_bindingContext = initDataBindings();

	}

	/*
	 * event handlers
	 */

	protected void onCopyAsStringSelected() {
		ArrayList<String> s = new ArrayList<String>();
		for (PathEntry p: getSelectedPathEntries()) {
			s.add(p.getPath());
		}
		StringSelection ss = new StringSelection(String.join("\n", s));
		Clipboard clip = Toolkit.getDefaultToolkit().getSystemClipboard();
		clip.setContents(ss, ss);
	}

	protected void onOpenSelected(SelectionEvent e) {
		DBPathEntry entry = getSelectedPathEntry();
		if (entry != null) {
			setLocationAndRefresh(entry);
		}
	}

	protected void onOpenInNewWindowSelected(SelectionEvent e) {
		DBPathEntry p = getSelectedPathEntry();
		if (p == null) {
			p = location.get().getPathEntry();
		}
		if (p != null) {
			new SwtFileFolderMenu().setLocationAndRefresh(p);
		} else if (location.get().getPathString() != null) {
			new SwtFileFolderMenu().setLocationAndRefresh(location.get().getPathString());
		} else if (location.get().getSearchString() != null) {
			new SwtFileFolderMenu().setLocationAndRefresh(location.get().getSearchString());
		} else if (location.get().getPathId() != 0L) {
			new SwtFileFolderMenu().setLocationAndRefresh(location.get().getPathId());
		}
	}

	protected void onOpenDuplicateDetailsSelected(SelectionEvent e) {
		DBPathEntry p = getSelectedPathEntry();
		if (p == null) {
			p = location.get().getPathEntry();
		}
		if (p != null) {
			new SwtDuplicateMenu().setLocationAndRefresh(p);
		} else if (location.get().getPathString() != null) {
			new SwtDuplicateMenu().setLocationAndRefresh(location.get().getPathString());
		} else if (location.get().getSearchString() != null) {
			new SwtDuplicateMenu().setLocationAndRefresh(location.get().getSearchString());
		} else if (location.get().getPathId() != 0L) {
			new SwtDuplicateMenu().setLocationAndRefresh(location.get().getPathId());
		}
	}

	protected void onNavigatePreviousSelected(SelectionEvent e) {
		location.navigatePrevious();
		setLocationAndRefresh(location.get());
	}

	protected void onNavigateNextSelected(SelectionEvent e) {
		location.navigateNext();
		setLocationAndRefresh(location.get());
	}

	protected void onUpperFolderSelected(SelectionEvent e) {
		DBPathEntry p = location.get().getPathEntry();
		if (p != null && p.getParentId() != 0L) {
			setLocationAndRefresh(p.getParentId());
		} else {
			writeStatusBar("Not ready for going up operation; be patient.");
		}
	}

	protected void onLocationModified(ModifyEvent arg0) {
		String newstring = txtLocation.getText();
		Assertion.assertNullPointerException(newstring != null);
		writeStatusBar(String.format("New path string is: %s", newstring));
		shell.setText(newstring);
		Location oldloc = location.get();
		if (newstring.equals(oldloc.getPathString())) {
			// noop
		} else if (newstring.equals(oldloc.getSearchString())) {
			oldloc.setPathEntry(null);
			oldloc.setPathId(0L);
			oldloc.setPathString(null);
		} else {
			Location newloc = new Location();
			newloc.setPathString(newstring);
			location.add(newloc);
		}
		refresh();
	}

	protected void onTableSelected(SelectionEvent e) {}

	private String order = PreferenceRW.getSwtFileFolderMenuSortOrder();
	private boolean isFolderChecked = true;
	private boolean isFileChecked = true;
	private boolean isCompressedFolderChecked = true;
	private boolean isCompressedFileChecked = true;

	protected void onTblclmnPathSelected(TableColumn tblclmnPath, SelectionEvent e) {
		if (table.getSortDirection() == SWT.UP) {
			order = "path";
		} else {
			order = "path DESC";
		}
		PreferenceRW.setSwtFileFolderMenuSortOrder(order);
		refresh();
	}

	protected void onTblclmnDateLastModifiedSelected(TableColumn tblclmnDateLastModified, SelectionEvent e) {
		if (table.getSortDirection() == SWT.UP) {
			order = "datelastmodified";
		} else {
			order = "datelastmodified DESC";
		}
		PreferenceRW.setSwtFileFolderMenuSortOrder(order);
		refresh();
	}

	protected void onTblclmnSizeSelected(TableColumn tblclmnSize, SelectionEvent e) {
		if (table.getSortDirection() == SWT.UP) {
			order = "size";
		} else {
			order = "size DESC";
		}
		PreferenceRW.setSwtFileFolderMenuSortOrder(order);
		refresh();
	}

	protected void onTblclmnCompressedsizeSelected(TableColumn tblclmnCompressedesize, SelectionEvent e) {
		if (table.getSortDirection() == SWT.UP) {
			order = "compressedsize";
		} else {
			order = "compressedsize DESC";
		}
		PreferenceRW.setSwtFileFolderMenuSortOrder(order);
		refresh();
	}

	protected void onTblclmnDuplicateSelected(TableColumn tblclmnDuplicate, SelectionEvent e) {
		if (table.getSortDirection() == SWT.UP) {
			order = "duplicate";
		} else {
			order = "duplicate DESC";
		}
		PreferenceRW.setSwtFileFolderMenuSortOrder(order);
		refresh();
	}

	protected void onTblclmnDedupablesizeSelected(TableColumn tblclmnDedupablesize, SelectionEvent e) {
		if (table.getSortDirection() == SWT.UP) {
			order = "dedupablesize";
		} else {
			order = "dedupablesize DESC";
		}
		PreferenceRW.setSwtFileFolderMenuSortOrder(order);
		refresh();
	}

	protected void onFoldersVisibleChecked(boolean checked) {
		isFolderChecked = checked;
		refresh();
	}

	protected void onFilesVisibleChecked(boolean checked) {
		isFileChecked = checked;
		refresh();
	}

	protected void onCompressedFoldersVisibleChecked(boolean checked) {
		isCompressedFolderChecked = checked;
		refresh();
	}

	protected void onCompressedFilesVisibleSelected(boolean checked) {
		isCompressedFileChecked = checked;
		refresh();
	}

	public void setLocationAndRefresh(final String text) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				txtLocation.setText(text); // onLocationModified() is automatically called here.
			}
		});
	}

	/*
	 * setLocationAndRefresh and related
	 */

	public void setLocationAndRefresh(final DBPathEntry entry) {
		Assertion.assertNullPointerException(entry != null);
		Assertion.assertNullPointerException(location != null);
		Location oldloc = location.get();
		if (oldloc.getPathEntry() != null && oldloc.getPathEntry().getPathId() == entry.getPathId()) {
			// noop
		} else if (oldloc.getPathString() != null && oldloc.getPathString().equals(entry.getPath())) {
			oldloc.setPathEntry(entry);
			oldloc.setPathId(entry.getPathId());
		} else {
			Location newloc = new Location();
			newloc.setPathEntry(entry);
			newloc.setPathId(entry.getPathId());
			newloc.setPathString(entry.getPath());
			location.add(newloc);
		}
		setLocationAndRefresh(entry.getPath());
	}

	public void setLocationAndRefresh(long id) {
		writeStatusBar(String.format("Starting query; new ID is: %d", id));
		Location oldloc = location.get();
		if (oldloc.getPathId() == id) {
			// null
		} else {
			Location newloc = new Location();
			newloc.setPathId(id);
			location.add(newloc);
		}
		refresh(new LazyRunnable() {
			@Override
			public void run() throws SQLException, InterruptedException {
				Debug.writelog("-- SwtFileFolderMenu SetLocationAndRefresh LOCAL PATTERN (id based) --");
				Location loc = location.get();
				DBPathEntry p = getDB().getDBPathEntryByPathId(loc.getPathId());
				if (p != null) {
					loc.setPathEntry(p);
					loc.setPathString(p.getPath());
					loc.setSearchString(null);
					setLocationAndRefresh(loc.getPathString());
				}
			}
		});
	}

	public void setLocationAndRefresh(final Location loc) {
		if (loc.getPathString() != null) {
			setLocationAndRefresh(loc.getPathString());
		} else if (loc.getPathEntry() != null) {
			setLocationAndRefresh(loc.getPathEntry().getPath());
		} else if (loc.getSearchString() != null) {
			setLocationAndRefresh(loc.getSearchString());
		} else {
			setLocationAndRefresh("");
		}
	}

	/*
	 * normal refresh
	 */

	private Scenario scenario = new Scenario();
	protected synchronized void refresh() {
		refresh(scenario);
	}

	class Scenario extends SwtCommonFileFolderMenu.Scenario {

		@Override
		public void run() throws SQLException, InterruptedException {
			writeProgress(10);
			Location loc = location.get();
			if (loc.getPathEntry() == null && loc.getSearchString() == null &&
					(loc.getPathEntry() != null || loc.getPathId() != 0L
					|| (loc.getPathString() != null && !"".equals(loc.getPathString())))) {

				writeProgress(50);
				if (loc.getPathString() != null) {
					DBPathEntry p = getDB().getDBPathEntryByPath(loc.getPathString());
					if (p != null) {
						loc.setPathEntry(p);
						loc.setPathId(p.getPathId());
						Debug.writelog("-- SwtFileFolderMenu PREPROCESS PATTERN 1 (path based entry detection) --");
					} else {
						loc.setSearchString(loc.getPathString());
						loc.setPathString(null);
						loc.setPathId(0L);
						loc.setPathEntry(null);
						Debug.writelog("-- SwtFileFolderMenu PREPROCESS PATTERN 2 (searchstring=" + loc.getSearchString() + ") --");
					}
				} else if (loc.getPathId() != 0L) {
					Debug.writelog("-- SwtFileFolderMenu PREPROCESS PATTERN 3 (id based) --");
					DBPathEntry p = getDB().getDBPathEntryByPathId(loc.getPathId());
					assert(p != null);
					setLocationAndRefresh(p);
					return;
				} else {
					Debug.writelog("-- SwtFileFolderMenu PREPROCESS PATTERN 4 (show all paths) --");
				}
			}

			try {
				threadWait();
				cleanupTable();

				ArrayList<String> typelist = new ArrayList<String> ();
				if (isFolderChecked) {
					typelist.add("type=0");
				}
				if (isFileChecked) {
					typelist.add("type=1");
				}
				if (isCompressedFolderChecked) {
					typelist.add("type=2");
				}
				if (isCompressedFileChecked) {
					typelist.add("type=3");
				}
				String typeWhere = typelist.size() == 0 ? "" : String.join(" OR ", typelist);

				threadWait();
				writeStatusBar("Querying...");
				writeProgress(70);

				String searchSubSQL;
				ArrayList<String> searchStringElement = new ArrayList<String> ();
				if (loc.getSearchString() == null || "".equals(loc.getSearchString())) {
					searchSubSQL = "";
				} else {
					ArrayList<String> p = new ArrayList<String> ();
					for (String s: loc.getSearchString().split(" ")) {
						if (! "".equals(s)) {
							p.add("path LIKE ?");
							searchStringElement.add(s);
						}
					}
					searchSubSQL = " AND (" + String.join(" AND ", p) + ")";
				}
				threadWait();
				DBPathEntry locationPathEntry = null;
				PreparedStatement ps;
				if (loc.getPathString() == null || "".equals(loc.getPathString())) {
					String sql = "SELECT * FROM directory AS d1 WHERE (" + typeWhere + ") " + searchSubSQL
							+ " AND (parentid=0 OR EXISTS (SELECT * FROM directory AS d2 WHERE d1.parentid=d2.pathid))"
							+ " ORDER BY " + order;
					Debug.writelog(sql);
					ps = getDB().prepareStatement(sql);
					int c = 1;
					for (String s: searchStringElement) {
						ps.setString(c, "%" + s + "%");
						Debug.writelog(c + " %" + s + "%");
						c++;
					}
				} else if ((locationPathEntry = loc.getPathEntry()) != null) {
					String sql = "SELECT * FROM directory AS d1 WHERE (" + typeWhere + ") " + searchSubSQL
							+ " AND (pathid=? OR EXISTS (SELECT * FROM upperlower WHERE upper=? AND lower=pathid))"
							+ " AND (parentid=0 OR EXISTS (SELECT * FROM directory AS d2 WHERE d1.parentid=d2.pathid))"
							+ " ORDER BY " + order;
					Debug.writelog(sql);
					ps = getDB().prepareStatement(sql);
					int c = 1;
					for (String s: searchStringElement) {
						ps.setString(c, "%" + s + "%");
						Debug.writelog(c + " %" + s + "%");
						c++;
					}
					ps.setLong(c++, locationPathEntry.getPathId());
					ps.setLong(c++, locationPathEntry.getPathId());
					Debug.writelog(locationPathEntry.getPath());
				} else {
					String sql = "SELECT * FROM directory AS d1 WHERE (" + typeWhere + ") " + searchSubSQL
							+ " AND path LIKE ?"
							+ " AND (parentid=0 OR EXISTS (SELECT * FROM directory AS d2 WHERE d1.parentid=d2.pathid))"
							+ " ORDER BY " + order;
					Debug.writelog(sql);
					ps = getDB().prepareStatement(sql);
					int c = 1;
					for (String s: searchStringElement) {
						ps.setString(c, "%" + s + "%");
						Debug.writelog(c + " %" + s + "%");
						c++;
					}
					ps.setString(c++, loc.getPathString() + "%");
					Debug.writelog(loc.getPathString());
				}

				try {
					LazyUpdater.Dispatcher disp = getDB().getDispatcher();
					disp.setList(Dispatcher.NONE);
					disp.setCsum(Dispatcher.NONE);

					ResultSet rs = ps.executeQuery();
					try {
						threadWait();
						Debug.writelog("QUERY FINISHED");
						writeStatusBar("Listing...");
						writeProgress(90);

						int count = 0;
						while (rs.next()) {
							threadWait();
							DBPathEntry p1 = getDB().rsToPathEntry(rs);
							Assertion.assertAssertionError(p1 != null);
							Assertion.assertAssertionError(p1.getPath() != null);
							if (locationPathEntry != null) {
								Assertion.assertAssertionError(locationPathEntry.getPath() != null);
								Assertion.assertAssertionError(p1.getPath().startsWith(locationPathEntry.getPath()),
										p1.getPath() + " does not start with " + locationPathEntry.getPath()
										);
							}
							PathEntry p2;
							try {
								p2 = disp.dispatch(p1);
							} catch (IOException e) {
								p2 = null;
							}
							if (p2 == null) {
								addRow(p1, rs.getInt("duplicate"), rs.getLong("dedupablesize"), true);
								getDB().unsetClean(p1.getParentId());
							} else {
								Assertion.assertAssertionError(p1.getPath().equals(p2.getPath()),
										"!! " + p1.getPath() + " != " + p2.getPath());
								if (!PathEntry.dscMatch(p1, p2)) {
									p1.setDateLastModified(p2.getDateLastModified());
									p1.setSize(p2.getSize());
									p1.setCompressedSize(p2.getCompressedSize());
									p1.clearCsum();
									getDB().unsetClean(p1.getParentId());
								}
								addRow(p1, rs.getInt("duplicate"), rs.getLong("dedupablesize"), false);
							}
							count ++;
						}
						writeStatusBar(String.format("%d items", count));
					} finally {
						rs.close();
					}
				} finally {
					ps.close();
				}
				writeProgress(0);
			} catch (WindowDisposedException e) {}
		}

		protected void cleanupTable() throws WindowDisposedException {
			if (table.isDisposed()) {
				throw new WindowDisposedException("!! Window disposed at cleanupTable");
			}
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					pathentrylist.clear();
					table.removeAll();;
				}
			});
		}

		protected void addRow(final DBPathEntry entry, final int duplicate,
				final long dedupablesize, final boolean grayout) throws WindowDisposedException {
			if (table.isDisposed()) {
				throw new WindowDisposedException("!! Window disposed at addRow");
			}
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					pathentrylist.add(entry);

					final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
					final NumberFormat numf = NumberFormat.getNumberInstance();
					Date d = new Date(entry.getDateLastModified());
					String[] row = {
							entry.getPath(),
							sdf.format(d),
							numf.format(entry.getSize()),
							numf.format(entry.getCompressedSize()),
							(duplicate > 0 ? numf.format(duplicate) : null),
							(dedupablesize > 0 ? numf.format(dedupablesize) : null),
					};

					final Display display = Display.getDefault();
					final Color blue = new Color(display, 0, 0, 255);
					final Color red = new Color(display, 255, 0, 0);
					final Color black = new Color(display, 0, 0, 0);
					final Color gray = new Color(display, 127, 127, 127);

					try {
						TableItem tableItem = new TableItem(table, SWT.NONE);
						tableItem.setText(row);
						if (grayout) {
							tableItem.setForeground(gray);
						} else if (entry.isNoAccess()) {
							tableItem.setForeground(red);
						} else if (entry.isFile() && entry.getSize() != entry.getCompressedSize()) {
							tableItem.setForeground(blue);
						} else {
							tableItem.setForeground(black);
						}

					} catch (Exception e) {
						if (!table.isDisposed()) {
							e.printStackTrace();
						}
					}
				}
			});
		}
	}

	protected DataBindingContext initDataBindings() {
		DataBindingContext bindingContext = new DataBindingContext();
		//
		IObservableValue observeBackgroundCompositeObserveWidget = WidgetProperties.background().observe(compositeToolBar);
		IObservableValue backgroundShellObserveValue = PojoProperties.value("background").observe(shell);
		bindingContext.bindValue(observeBackgroundCompositeObserveWidget, backgroundShellObserveValue, null, null);
		//
		IObservableValue observeBackgroundLblStatusBarObserveWidget = WidgetProperties.background().observe(lblStatusBar);
		bindingContext.bindValue(observeBackgroundLblStatusBarObserveWidget, backgroundShellObserveValue, null, null);
		//
		IObservableValue observeBackgroundCompositeStatusBarObserveWidget = WidgetProperties.background().observe(compositeStatusBar);
		bindingContext.bindValue(observeBackgroundCompositeStatusBarObserveWidget, backgroundShellObserveValue, null, null);
		//
		return bindingContext;
	}
}
