<template>
  <div class="mydata-panel" @click="closeMenu">
    <div class="md-content md-content--split">
      <div class="md-page-toolbar">
        <div class="md-page-toolbar-left">
          <div class="md-page-title">我的数据集</div>
          <div class="md-page-summary">共 {{ libraryTotalCount }} 个</div>
        </div>
        <div class="md-page-toolbar-actions">
          <button class="md-page-btn" @click.stop="$emit('upload')">
            <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M8 10.5V2.5M5 5.5l3-3 3 3M2.5 12.5v1h11v-1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            上传数据
          </button>
          <button class="md-page-btn md-page-btn--ghost" @click.stop="showNewFolder = true">
            <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
            新建文件夹
          </button>
        </div>
      </div>

      <div class="md-workspace-grid" :class="{ 'md-workspace-grid--library-expanded': libraryExpanded }">
        <aside class="md-library-pane" :class="{ 'md-library-pane--expanded': libraryExpanded }">
          <div class="md-library-head">
            <div class="md-library-head-info">
              <div class="md-pane-title">数据集库</div>
              <div class="md-pane-sub">未归类 {{ visibleDataSets.length }} / {{ libraryTotalCount }}</div>
            </div>
            <div class="md-library-head-actions">
              <button class="md-icon-btn" @click.stop="libraryExpanded = !libraryExpanded">
                <svg v-if="!libraryExpanded" width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M6 3H3v10h10v-3M9 3h4v4M8 8l5-5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <svg v-else width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M13 6V3H3v10h3M8 8 3 13M3 9v4h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {{ libraryExpanded ? '收起' : '展开' }}
              </button>
              <button class="md-icon-btn" @click.stop="showNewFolder = true">
                <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
                新建
              </button>
              <button class="md-icon-btn md-icon-btn--upload" @click.stop="$emit('upload')">
                <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M8 10.5V2.5M5 5.5l3-3 3 3M2.5 12.5v1h11v-1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
                上传
              </button>
            </div>
          </div>

          <div v-if="libraryHasItems" class="md-dataset-tools md-dataset-tools--library" @click.stop>
            <template v-if="selectedSessionIds.size">
              <div class="md-batch-bar">
                <span class="md-batch-count">已选 {{ selectedSessionIds.size }} 项</span>
                <button class="md-batch-btn" @click="selectAllVisible">全选</button>
                <button class="md-batch-btn" @click="clearSelection">取消</button>
                <div class="md-batch-sep"></div>
                <button class="md-batch-btn" @click="openBatchMoveDialog">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
                  移动到
                </button>
                <button class="md-batch-btn md-batch-btn--danger" @click="confirmBatchDelete">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 4h12M5 4V2h6v2M6 7v5M10 7v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M3 4l1 10h8l1-10" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
                  删除
                </button>
              </div>
            </template>
            <template v-else>
              <div class="md-dataset-search">
                <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.2"/><path d="M10.5 10.5 14 14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
                <input v-model="datasetSearch" placeholder="搜索名称或文件名" />
              </div>
              <select v-model="datasetSort" class="md-dataset-sort" aria-label="数据集排序">
                <option value="recent">最近使用</option>
                <option value="created">创建时间</option>
                <option value="name">名称</option>
                <option value="versions">版本数</option>
                <option value="results">分析数</option>
              </select>
            </template>
          </div>

          <div class="md-library-scroll">
            <template v-if="libraryHasItems">
              <div v-if="folders.length" class="md-library-group">
                <MyDataFolderCard
                  v-for="folder in folders"
                  :key="folder.id"
                  v-model="renamingValue"
                  :drop-active="activeFolderDropId === folder.id"
                  :file-count="folderDataSets(folder).length"
                  :folder="folder"
                  :open="!!openFolders[folder.id]"
                  :renaming="renamingFolderId === folder.id"
                  :total-file-count="folderTotalCount(folder)"
                  @toggle="toggleFolder"
                  @open-menu="openFolderMenu"
                  @card-drag-over="onFolderCardDragOver"
                  @card-drag-leave="onFolderCardDragLeave"
                  @drop-card="onDropToFolderCard"
                  @confirm-rename="confirmRenameFolder"
                  @cancel-rename="renamingFolderId = ''"
                />
              </div>

              <div v-for="folder in folders" :key="'body-'+folder.id">
                <div v-if="openFolders[folder.id]" class="md-folder-expand" :class="{ 'md-folder-expand--active': activeFolderDropId === folder.id }">
                  <div class="md-folder-expand-head">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="md-folder-icon-sm"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" fill="#fef3c7"/></svg>
                    <span>{{ folder.name }}</span>
                    <button class="md-folder-close" @click="openFolders[folder.id] = false">&times;</button>
                  </div>
                  <div
                    class="md-folder-dropzone"
                    @dragover.prevent="onFolderBodyDragOver(folder.id)"
                    @dragleave="onFolderBodyDragLeave($event, folder.id)"
                    @drop.prevent="onDropToFolderBody($event, folder.id)"
                  >
                    <div v-if="!folderDataSets(folder).length" class="md-folder-empty">{{ datasetSearch ? '该文件夹没有匹配的数据集' : '拖拽数据卡片到文件夹即可归类' }}</div>
                    <div v-else class="md-card-grid md-card-grid--library">
                      <MyDataSetCard
                        v-for="ds in folderDataSets(folder)"
                        :key="ds.sessionId"
                        v-model="renamingValue"
                        :data-set="ds"
                        :format-date="formatDate"
                        :in-folder="true"
                        :renaming="renamingDsId === ds.sessionId"
                        :selectable="true"
                        :selected="selectedSessionIds.has(ds.sessionId)"
                        @switch="$emit('switch-session', $event)"
                        @open-menu="openDsMenu"
                        @open-menu-button="openDsMenuByButton"
                        @drag-start="onDragStart"
                        @select="toggleSelect"
                        @confirm-rename="confirmRenameDs"
                        @cancel-rename="renamingDsId = ''"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div
                class="md-ungrouped-dropzone"
                :class="{ 'md-ungrouped-dropzone--active': ungroupedDropActive }"
                @dragover.prevent="onUngroupedDragOver"
                @dragleave="onUngroupedDragLeave"
                @drop.prevent="onDropToUngrouped"
              >
                <div class="md-library-group-title">未归类</div>
                <div v-if="ungroupedDataSets.length" class="md-card-grid md-card-grid--library">
                  <MyDataSetCard
                    v-for="ds in ungroupedDataSets"
                    :key="ds.sessionId"
                    v-model="renamingValue"
                    :data-set="ds"
                    :format-date="formatDate"
                    :renaming="renamingDsId === ds.sessionId"
                    :selectable="true"
                    :selected="selectedSessionIds.has(ds.sessionId)"
                    @switch="$emit('switch-session', $event)"
                    @open-menu="openDsMenu"
                    @open-menu-button="openDsMenuByButton"
                    @drag-start="onDragStart"
                    @select="toggleSelect"
                    @confirm-rename="confirmRenameDs"
                    @cancel-rename="renamingDsId = ''"
                  />
                </div>
                <div v-else class="md-folder-empty">{{ datasetSearch ? '未归类中没有匹配的数据集' : '暂无未归类数据集' }}</div>
              </div>

              <div v-if="!libraryVisibleCount" class="md-empty md-empty--library">
                <div>没有匹配的数据集</div>
                <button class="md-empty-action" @click.stop="datasetSearch = ''">清空搜索</button>
              </div>
            </template>
            <div v-else class="md-empty md-empty--library">
              <div>还没有数据集</div>
              <button class="md-empty-action" @click.stop="$emit('upload')">上传数据</button>
            </div>
          </div>

          <!-- 分页控件：固定在面板底部，不随列表滚动 -->
          <div v-if="datasetTotal > 0" class="md-pagination">
            <div class="md-page-size">
              <span>每页</span>
              <select :value="datasetPageSize" @change="onPageSizeChange($event.target.value)">
                <option :value="50">50</option>
                <option :value="100">100</option>
                <option :value="200">200</option>
                <option :value="500">500</option>
              </select>
              <span>条</span>
            </div>
            <div class="md-page-info">{{ datasetPage }} / {{ totalPages }} 页（共 {{ datasetTotal }} 条）</div>
            <div class="md-page-btns">
              <button :disabled="datasetPage <= 1" class="md-page-btn" @click="goPage(datasetPage - 1)">上一页</button>
              <button :disabled="datasetPage >= totalPages" class="md-page-btn" @click="goPage(datasetPage + 1)">下一页</button>
            </div>
          </div>
        </aside>

        <main class="md-detail-pane">
          <template v-if="currentSessionId">
            <section class="md-dataset-summary">
              <div class="md-dataset-summary-main">
                <div class="md-dataset-summary-title">
                  <span>{{ currentDataSetName || '未命名数据集' }}</span>
                  <span v-if="currentDatasetVersionNo || currentDataSet?.currentVersionNo" class="md-current-bar-version">v{{ currentDatasetVersionNo || currentDataSet?.currentVersionNo }}</span>
                </div>
                <div class="md-dataset-summary-stats">
                  <span>{{ totalRows || currentDataSet?.rowCount || 0 }} 行</span>
                  <span>{{ variables.length || currentDataSet?.columnCount || 0 }} 个变量</span>
                  <span>{{ currentDataSet?.versionCount || datasetVersions.length || 0 }} 个版本</span>
                  <span>{{ currentDataSet?.resultCount || historyItems.length || 0 }} 条分析</span>
                </div>
              </div>
              <div class="md-dataset-summary-actions">
                <button class="md-bar-btn md-bar-btn--teal" @click="$emit('go-processing', currentSessionId)">
                  <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M2 2h5v5H2zM9 2h5v5H9zM2 9h5v5H2zM9 9h5v5H9z" stroke="currentColor" stroke-width="1.1"/></svg>
                  数据处理
                </button>
                <button class="md-bar-btn md-bar-btn--blue" @click="$emit('go-analysis', currentSessionId)">
                  <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M2 14V6l3-4h6l3 4v8H2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/><path d="M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
                  数据分析
                </button>
                <button class="md-page-btn md-page-btn--ghost" @click.stop="showDatasetDetail = true">
                  <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.2"/><path d="M8 7.2v4M8 4.6h.01" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
                  数据集详情
                </button>
              </div>
            </section>

            <div class="md-detail-tabs">
              <button class="md-detail-tab" :class="{ 'md-detail-tab--active': detailTab === 'preview' }" @click="detailTab = 'preview'">
                数据预览 <span v-if="previewRows.length">{{ previewRows.length }}</span>
              </button>
              <button class="md-detail-tab" :class="{ 'md-detail-tab--active': detailTab === 'versions' }" @click="detailTab = 'versions'">
                版本历史 <span v-if="datasetVersions.length">{{ datasetVersions.length }}</span>
              </button>
              <button class="md-detail-tab" :class="{ 'md-detail-tab--active': detailTab === 'history' }" @click="detailTab = 'history'">
                分析记录 <span v-if="historyItems.length">{{ historyItems.length }}</span>
              </button>
            </div>

            <section class="md-detail-surface">
              <div v-if="detailTab === 'preview'" style="flex:1;min-height:0;display:flex;flex-direction:column;">
                <div v-if="previewLoading" class="md-empty-hint"><span>正在加载数据预览...</span></div>
                <div v-else-if="previewError" class="md-empty-hint md-empty-hint--error">
                  <span>{{ previewError }}</span>
                </div>
                <div v-else-if="previewHeaders.length" class="md-preview-table md-preview-table--split">
                  <DataPreviewGrid
                    :headers="previewHeaders"
                    :display-headers="displayPreviewHeaders"
                    :display-rows="displayPreviewRows"
                  />
                </div>
                <div v-else class="md-empty-hint"><span>暂无可预览数据</span></div>
              </div>

              <div v-else-if="detailTab === 'versions'" class="md-version-shell">
                <div v-if="versionsLoading" class="md-empty-hint"><span>正在加载数据版本...</span></div>
                <div v-else-if="datasetVersions.length" class="md-version-list md-version-list--detail">
                  <div
                    v-for="version in datasetVersions"
                    :key="version.id"
                    class="md-version-item md-version-item--row"
                    :class="{ 'md-version-item--current': isCurrentVersion(version) }"
                    @click.stop="!renamingVersionId && activateVersion(version)"
                  >
                    <span class="md-version-name">v{{ version.version_no }}</span>
                    <span class="md-version-title-cell">
                      <template v-if="renamingVersionId !== version.id">
                        <span
                          class="md-version-filename"
                          aria-label="版本名称，双击也可以重命名"
                          data-tooltip="版本名称，双击也可以重命名"
                          @dblclick.stop="startRenameVersion(version)"
                        >{{ versionDisplayName(version) }}</span>
                        <button
                          class="md-version-rename-btn"
                          type="button"
                          aria-label="重命名版本名称"
                          data-tooltip="重命名版本名称"
                          @click.stop="startRenameVersion(version)"
                        >
                          <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M3 11.5V13h1.5l7-7-1.5-1.5-7 7zM9.5 5 11 3.5 12.5 5 11 6.5" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
                          重命名
                        </button>
                        <button
                          class="md-version-copy-btn"
                          type="button"
                          aria-label="复制这个版本"
                          data-tooltip="复制这个版本"
                          @click.stop="copyVersion(version)"
                        >
                          <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                            <path d="M5.5 5.5h6v7h-6zM3.5 10.5h-1v-8h7v1" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/>
                          </svg>
                          复制
                        </button>
                        <button
                          class="md-version-delete-btn"
                          type="button"
                          :disabled="isCurrentVersion(version)"
                          :aria-label="isCurrentVersion(version) ? '当前版本不能删除，请先切换到其他版本' : '删除版本'"
                          :data-tooltip="isCurrentVersion(version) ? '当前版本不能删除，请先切换到其他版本' : '删除版本'"
                          @click.stop="deleteVersion(version)"
                        >
                          <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                            <path d="M3.5 4.5h9M6.5 4.5V3h3v1.5M5 6v6.5h6V6" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          删除
                        </button>
                      </template>
                      <input
                        v-else
                        ref="versionRenameInputRef"
                        class="md-version-rename-input"
                        :value="renamingVersionName"
                        @input="renamingVersionName = $event.target.value"
                        @keydown.enter.stop="commitRenameVersion(version)"
                        @keydown.escape.stop="cancelRenameVersion"
                        @blur.stop="commitRenameVersion(version)"
                        @click.stop
                      />
                    </span>
                    <span
                      class="md-version-source"
                      :class="{ 'md-version-source--initial': isInitialVersion(version) }"
                      :aria-label="versionSourceTitle(version)"
                      :data-tooltip="versionSourceTitle(version)"
                    >{{ versionSource(version) }}</span>
                    <button
                      class="md-version-analysis"
                      :class="{ 'md-version-analysis--empty': !versionHistoryCount(version) }"
                      type="button"
                      :disabled="!versionHistoryCount(version)"
                      :aria-label="versionAnalysisTitle(version)"
                      :data-tooltip="versionAnalysisTitle(version)"
                      @click.stop="viewVersionHistory(version)"
                    >{{ versionHistoryCount(version) }} 条分析</button>
                    <span class="md-version-meta">{{ versionSummary(version) }}</span>
                    <span class="md-version-date">{{ formatDate(version.created_at) }}</span>
                    <span v-if="isCurrentVersion(version)" class="md-version-current">当前</span>
                  </div>
                </div>
                <div v-else class="md-empty-hint"><span>暂无版本记录</span></div>
              </div>

              <div v-else class="md-history-shell">
                <div class="md-history-workspace">
                  <aside class="md-history-list-pane">
                    <div class="md-history-head">
                      <div class="md-section-note">
                        当前 {{ currentVersionHistoryCount }} / 全部 {{ historyItems.length }}
                      </div>
                      <span v-if="historyItems.length" class="md-filter-tabs">
                        <button class="md-filter-tab" :class="{ 'md-filter-tab--active': historyFilter === 'current' }" @click="historyFilter = 'current'">当前版本</button>
                        <button class="md-filter-tab" :class="{ 'md-filter-tab--active': historyFilter === 'all' }" @click="historyFilter = 'all'">全部版本</button>
                      </span>
                    </div>
                    <div v-if="visibleHistoryItems.length" class="md-history-list">
                      <button
                        v-for="(item, idx) in visibleHistoryItems"
                        :key="item.id || idx"
                        class="md-history-item"
                        :class="{ 'md-history-item--active': expandedResultIdx === idx, 'md-history-item--stale': !isCurrentHistoryItem(item) }"
                        @click="toggleResult(idx)"
                      >
                        <span class="md-history-icon">
                          <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M2 6h12" stroke="currentColor" stroke-width="1" opacity=".5"/></svg>
                        </span>
                        <span class="md-history-name">{{ item.name }}</span>
                        <span v-if="item.dataset_version_no" class="md-tag-version" :class="{ 'md-tag-version--current': isCurrentHistoryItem(item) }">v{{ item.dataset_version_no }}</span>
                      </button>
                    </div>
                    <div v-else-if="historyItems.length" class="md-empty-hint"><span>当前版本暂无分析记录，可切换到「全部版本」查看旧版本结果</span></div>
                    <div v-else class="md-empty-hint"><span>该数据集暂无分析记录</span></div>
                  </aside>

                  <section class="md-history-detail-pane">
                    <MyDataResultExpand
                      v-if="expandedResultIdx >= 0 && expandedResult"
                      :result="expandedResult"
                      :results="displayExpandedResults"
                      @close="closeExpandedResult"
                    />
                    <div v-else class="md-empty md-empty--history-detail">
                      <div>{{ visibleHistoryItems.length ? '选择一条分析记录查看结果' : '暂无可查看的分析结果' }}</div>
                      <button class="md-empty-action" @click.stop="$emit('go-analysis', currentSessionId)">去数据分析</button>
                    </div>
                  </section>
                </div>
              </div>
            </section>
          </template>
          <div v-else class="md-empty md-empty--detail">
            <div>请选择一个数据集</div>
            <p>从左侧数据集库选择已有数据，或上传一个新数据集开始分析。</p>
            <button class="md-empty-action" @click.stop="$emit('upload')">上传数据</button>
          </div>
        </main>
      </div>
    </div>

    <MyDataContextMenu
      :context-menu="contextMenu"
      :folders="folders"
      @start-rename-ds="startRenameDs"
      @start-rename-folder="startRenameFolder"
      @delete-folder="deleteFolder"
      @move-ds-to-folder="moveDsToFolder"
      @go-processing="emitDsAction('go-processing', $event)"
      @go-analysis="emitDsAction('go-analysis', $event)"
      @export-dataset="emitDsAction('export-dataset', $event)"
      @copy-dataset="emitDsAction('copy-dataset', $event)"
      @delete-dataset="emitDsAction('delete-dataset', $event)"
    />

    <div v-if="showNewFolder" class="upload-overlay" @click.self="showNewFolder = false">
      <div class="upload-modal md-new-folder-modal">
        <div class="upload-modal-head">
          <span>新建文件夹</span>
          <button class="upload-modal-close" @click="showNewFolder = false">&times;</button>
        </div>
        <div class="md-new-folder-body">
          <input ref="newFolderInput" v-model="newFolderName" class="md-new-folder-input" placeholder="文件夹名称"
            @keydown.enter="confirmNewFolder" @keydown.escape="showNewFolder = false" />
          <div class="md-new-folder-actions">
            <button class="md-page-btn md-page-btn--ghost" @click="newFolderName = ''; showNewFolder = false">取消</button>
            <button class="md-page-btn" @click="confirmNewFolder">确定</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDatasetDetail" class="upload-overlay" @click.self="showDatasetDetail = false">
      <div class="upload-modal md-detail-modal">
        <div class="upload-modal-head">
          <span>数据集详情</span>
          <button class="upload-modal-close" @click="showDatasetDetail = false">&times;</button>
        </div>
        <div class="md-detail-body">
          <div class="md-detail-hero">
            <div>
              <div class="md-detail-name">{{ currentDataSetName || '未命名数据集' }}</div>
              <div class="md-detail-sub">{{ currentDataSet?.fileName || dataFileName || '暂无原始文件名' }}</div>
            </div>
            <span v-if="currentDatasetVersionNo || currentDataSet?.currentVersionNo" class="md-detail-version">
              v{{ currentDatasetVersionNo || currentDataSet?.currentVersionNo }}
            </span>
          </div>

          <div class="md-detail-stats">
            <div v-for="item in datasetDetailStats" :key="item.label" class="md-detail-stat">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>

          <div class="md-detail-section">
            <div class="md-detail-section-title">处理链路</div>
            <div v-if="datasetLineage.length" class="md-lineage">
              <template v-for="(version, index) in datasetLineage" :key="version.id">
                <div class="md-lineage-node" :class="{ 'md-lineage-node--current': isCurrentVersion(version) }">
                  <span class="md-lineage-version">v{{ version.version_no }}</span>
                  <span
                    class="md-lineage-source"
                    :class="{ 'md-lineage-source--initial': isInitialVersion(version) }"
                    :aria-label="versionSourceTitle(version)"
                    :data-tooltip="versionSourceTitle(version)"
                  >{{ versionSource(version) }}</span>
                  <span class="md-lineage-meta">{{ versionSummary(version) }}</span>
                </div>
                <div v-if="index < datasetLineage.length - 1" class="md-lineage-arrow">→</div>
              </template>
            </div>
            <div v-else class="md-empty-hint">暂无处理链路</div>
          </div>

          <div class="md-detail-section">
            <div class="md-detail-section-title">字段结构</div>
            <div v-if="variables.length" class="md-detail-var-table">
              <div class="md-detail-var-head">
                <span>变量名</span>
                <span>显示名</span>
                <span>类型</span>
                <span>测量</span>
                <span>标签</span>
              </div>
              <div v-for="variable in variables" :key="variable.name" class="md-detail-var-row">
                <span class="md-tooltip" :aria-label="variable.name" :data-tooltip="variable.name">{{ variable.name }}</span>
                <span class="md-tooltip" :aria-label="variable.display_name || variable.name" :data-tooltip="variable.display_name || variable.name">{{ variable.display_name || variable.name }}</span>
                <span>{{ variableTypeLabel(variable) }}</span>
                <span>{{ measureLabel(variable) }}</span>
                <span>{{ valueLabelCount(variable) }}</span>
              </div>
            </div>
            <div v-else class="md-empty-hint">暂无字段结构信息</div>
          </div>

          <div class="md-detail-section">
            <div class="md-detail-section-title">版本摘要</div>
            <div v-if="datasetVersions.length" class="md-detail-version-list">
              <div v-for="version in datasetVersions" :key="version.id" class="md-detail-version-row">
                <span>v{{ version.version_no }}</span>
                <span>{{ versionSource(version) }}</span>
                <span>{{ versionSummary(version) }}</span>
                <span>{{ formatDate(version.created_at) }}</span>
              </div>
            </div>
            <div v-else class="md-empty-hint">暂无版本记录</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showBatchMoveDialog" class="upload-overlay" @click.self="showBatchMoveDialog = false">
      <div class="upload-modal md-batch-move-modal">
        <div class="upload-modal-head">
          <span>批量移动到文件夹</span>
          <button class="upload-modal-close" @click="showBatchMoveDialog = false">&times;</button>
        </div>
        <div class="md-batch-move-body">
          <div class="md-batch-move-hint">已选 {{ selectedSessionIds.size }} 个数据集</div>
          <div class="md-batch-move-options">
            <label class="md-batch-move-option" :class="{ 'md-batch-move-option--active': !batchMoveTargetFolderId }">
              <input v-model="batchMoveTargetFolderId" type="radio" :value="null" />
              <span>未归类（移出文件夹）</span>
            </label>
            <label
              v-for="folder in folders"
              :key="folder.id"
              class="md-batch-move-option"
              :class="{ 'md-batch-move-option--active': batchMoveTargetFolderId === folder.id }"
            >
              <input v-model="batchMoveTargetFolderId" type="radio" :value="folder.id" />
              <span>{{ folder.name }}</span>
            </label>
          </div>
          <div class="md-batch-move-actions">
            <button class="md-page-btn md-page-btn--ghost" @click="showBatchMoveDialog = false">取消</button>
            <button class="md-page-btn" @click="executeBatchMove">确定移动</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pendingCopyVersion" class="upload-overlay" @click.self="cancelCopyVersion">
      <div class="upload-modal md-version-copy-modal">
        <div class="upload-modal-head">
          <span>复制版本</span>
          <button class="upload-modal-close" @click="cancelCopyVersion">&times;</button>
        </div>
        <div class="md-version-copy-body">
          <label class="md-version-copy-label" for="version-copy-name">版本名称</label>
          <div class="md-version-copy-field">
            <input
              id="version-copy-name"
              ref="versionCopyInputRef"
              v-model="copyVersionName"
              class="md-version-copy-input"
              placeholder="请输入"
              @keydown.enter.stop="confirmCopyVersion"
              @keydown.escape.stop="cancelCopyVersion"
            />
            <button class="md-version-copy-original" type="button" @click="useOriginalVersionName">
              使用原名称
            </button>
          </div>
        </div>
        <div class="md-version-copy-actions">
          <button class="md-page-btn md-page-btn--ghost" @click="cancelCopyVersion">取消</button>
          <button class="md-version-copy-confirm" :disabled="!copyVersionName.trim()" @click="confirmCopyVersion">复制</button>
        </div>
      </div>
    </div>

    <div v-if="pendingDeleteVersion" class="upload-overlay" @click.self="cancelDeleteVersion">
      <div class="upload-modal md-version-delete-modal">
        <div class="upload-modal-head">
          <span>删除版本</span>
          <button class="upload-modal-close" @click="cancelDeleteVersion">&times;</button>
        </div>
        <div class="md-version-delete-body">
          <div class="md-version-delete-icon">
            <svg width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M3.5 4.5h9M6.5 4.5V3h3v1.5M5 6v6.5h6V6" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="md-version-delete-copy">
            <strong>确定删除「{{ versionDisplayName(pendingDeleteVersion) }}」吗？</strong>
            <p>
              <template v-if="versionHistoryCount(pendingDeleteVersion)">
                这个版本关联的 {{ versionHistoryCount(pendingDeleteVersion) }} 条分析记录也会一起删除。
              </template>
              <template v-else>删除后不可恢复。</template>
            </p>
          </div>
        </div>
        <div class="md-version-delete-actions">
          <button class="md-page-btn md-page-btn--ghost" @click="cancelDeleteVersion">取消</button>
          <button class="md-version-delete-confirm" @click="confirmDeleteVersion">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import MyDataContextMenu from './MyDataContextMenu.vue'
import MyDataFolderCard from './MyDataFolderCard.vue'
import MyDataResultExpand from './MyDataResultExpand.vue'
import MyDataSetCard from './MyDataSetCard.vue'
import DataPreviewGrid from '../../data-processing/components/DataPreviewGrid.vue'
import { processingMethodMap } from '../../data-processing/methodRegistry.js'
import * as api from '../../api.js'
import { useExpandedResults } from '../../composables/data/useExpandedResults.js'
import { useMyDataFolders } from '../../composables/data/useMyDataFolders.js'
import { formatShortDateTime } from '../../utils/dateFormat.js'

const props = defineProps({
  dataFileName: { type: String, default: '' },
  totalRows: { type: Number, default: 0 },
  variables: { type: Array, default: () => [] },
  historyItems: { type: Array, default: () => [] },
  allDataSets: { type: Array, default: () => [] },
  currentSessionId: { type: String, default: '' },
  currentDatasetVersionId: { type: [Number, String], default: null },
  currentDatasetVersionNo: { type: [Number, String], default: null },
  folders: { type: Array, default: () => [] },
  datasetPage: { type: Number, default: 1 },
  datasetPageSize: { type: Number, default: 50 },
  datasetTotal: { type: Number, default: 0 },
  folderDataSetsAll: { type: Array, default: () => [] },
})
const emit = defineEmits([
  'open-result', 'switch-session', 'create-folder', 'delete-folder',
  'rename-folder', 'move-to-folder', 'rename-dataset',
  'go-analysis', 'go-processing', 'delete-dataset',
  'export-dataset', 'copy-dataset', 'upload', 'activate-version',
  'refresh-datasets', 'version-copied', 'version-deleted', 'change-page',
])

const datasetVersions = ref([])
const datasetSearch = ref('')
const datasetSort = ref('recent')
const detailTab = ref('preview')
const historyFilter = ref('current')
const libraryExpanded = ref(false)
const previewHeaders = ref([])
const previewLoading = ref(false)
const previewRows = ref([])
const previewError = ref('')
const showDatasetDetail = ref(false)
const versionSourceJobs = ref({})
const versionsLoading = ref(false)
const selectedSessionIds = ref(new Set())
const showBatchMoveDialog = ref(false)
const batchMoveTargetFolderId = ref(null)
const renamingVersionId = ref(null)
const renamingVersionName = ref('')
const versionRenameInputRef = ref(null)
const pendingDeleteVersion = ref(null)
const pendingCopyVersion = ref(null)
const copyVersionName = ref('')
const versionCopyInputRef = ref(null)

const libraryDataSets = computed(() => [...props.allDataSets, ...props.folderDataSetsAll])
const currentDataSet = computed(() => libraryDataSets.value.find(item => item.sessionId === props.currentSessionId))

const currentDataSetName = computed(() => currentDataSet.value?.topic || currentDataSet.value?.fileName || props.dataFileName)

const visibleDataSets = computed(() => {
  const keyword = datasetSearch.value.trim().toLowerCase()
  const items = props.allDataSets.filter(item => {
    if (!keyword) return true
    return [item.topic, item.fileName].some(value => String(value || '').toLowerCase().includes(keyword))
  })
  return items.slice().sort((a, b) => compareDataSets(a, b, datasetSort.value))
})

const visibleFolderDataSetsAll = computed(() => {
  const keyword = datasetSearch.value.trim().toLowerCase()
  const items = props.folderDataSetsAll.filter(item => {
    if (!keyword) return true
    return [item.topic, item.fileName].some(value => String(value || '').toLowerCase().includes(keyword))
  })
  return items.slice().sort((a, b) => compareDataSets(a, b, datasetSort.value))
})

const libraryTotalCount = computed(() => props.datasetTotal + props.folderDataSetsAll.length)
const libraryVisibleCount = computed(() => visibleDataSets.value.length + visibleFolderDataSetsAll.value.length)
const libraryHasItems = computed(() => Boolean(props.folders.length || libraryTotalCount.value))

const variableMetaMap = computed(() => {
  const map = {}
  for (const variable of props.variables) {
    map[variable.name] = variable
  }
  return map
})

const displayPreviewHeaders = computed(() => previewHeaders.value.map(header => {
  const variable = variableMetaMap.value[header]
  return variable?.display_name || header
}))

const displayPreviewRows = computed(() => previewRows.value.map(row => row.map((cell, index) => {
  const header = previewHeaders.value[index]
  return formatPreviewCell(variableMetaMap.value[header], cell)
})))

const currentVersionHistoryCount = computed(() => props.historyItems.filter(isCurrentHistoryItem).length)
const totalPages = computed(() => Math.max(1, Math.ceil(props.datasetTotal / props.datasetPageSize)))

function goPage(page) {
  const target = Math.max(1, Math.min(totalPages.value, page))
  if (target !== props.datasetPage) {
    emit('change-page', target, props.datasetPageSize)
    clearSelection()
  }
}

function onPageSizeChange(size) {
  const newSize = Math.max(1, parseInt(size, 10) || 50)
  emit('change-page', 1, newSize)
  clearSelection()
}
const datasetLineage = computed(() => datasetVersions.value.slice().sort((a, b) => Number(a.version_no || 0) - Number(b.version_no || 0)))
const visibleHistoryItems = computed(() => {
  if (historyFilter.value === 'all') return props.historyItems
  return props.historyItems.filter(isCurrentHistoryItem)
})
const datasetDetailStats = computed(() => [
  { label: '行数', value: `${props.totalRows || currentDataSet.value?.rowCount || 0}` },
  { label: '字段', value: `${props.variables.length || currentDataSet.value?.columnCount || 0}` },
  { label: '版本', value: `${currentDataSet.value?.versionCount || datasetVersions.value.length || 0}` },
  { label: '分析', value: `${currentDataSet.value?.resultCount || props.historyItems.length || 0}` },
  { label: '大小', value: currentDataSet.value?.fileSize || '-' },
  { label: '创建时间', value: formatDate(currentDataSet.value?.createdAt) || '-' },
])

const {
  closeExpandedResult,
  displayExpandedResults,
  expandedResult,
  expandedResultIdx,
  toggleResult,
} = useExpandedResults(props, visibleHistoryItems)
const {
  activeFolderDropId,
  closeMenu,
  confirmNewFolder,
  confirmRenameDs,
  confirmRenameFolder,
  contextMenu,
  deleteFolder,
  moveDsToFolder,
  newFolderInput,
  newFolderName,
  onDragStart,
  onDropToFolderBody,
  onDropToFolderCard,
  onDropToUngrouped,
  onFolderBodyDragLeave,
  onFolderBodyDragOver,
  onFolderCardDragLeave,
  onFolderCardDragOver,
  onUngroupedDragLeave,
  onUngroupedDragOver,
  openDsMenu,
  openDsMenuByButton,
  openFolderMenu,
  openFolders,
  renamingDsId,
  renamingFolderId,
  renamingValue,
  showNewFolder,
  startRenameDs,
  startRenameFolder,
  toggleFolder,
  ungroupedDataSets,
  ungroupedDropActive,
} = useMyDataFolders(props, emit, { allDataSets: visibleDataSets })

function formatDate(ts) {
  return formatShortDateTime(ts)
}

function compareDataSets(a, b, sortKey) {
  if (sortKey === 'name') {
    return String(a.topic || a.fileName || '').localeCompare(String(b.topic || b.fileName || ''), 'zh-Hans')
  }
  if (sortKey === 'versions') return Number(b.versionCount || 0) - Number(a.versionCount || 0)
  if (sortKey === 'results') return Number(b.resultCount || 0) - Number(a.resultCount || 0)
  if (sortKey === 'created') return Number(b.createdAt || 0) - Number(a.createdAt || 0)
  return Number(b.lastUsedAt || b.createdAt || 0) - Number(a.lastUsedAt || a.createdAt || 0)
}

function folderTotalCount(folder) {
  const sessionIds = new Set(folder.sessionIds || [])
  return props.folderDataSetsAll.filter(dataSet => sessionIds.has(dataSet.sessionId)).length
}

function folderDataSets(folder) {
  const sessionIds = new Set(folder.sessionIds || [])
  return visibleFolderDataSetsAll.value.filter(dataSet => sessionIds.has(dataSet.sessionId))
}

function summaryCount(summary, ...keys) {
  if (!summary) return 0
  for (const key of keys) {
    const value = Number(summary[key])
    if (Number.isFinite(value) && value > 0) return value
  }
  return 0
}

function versionSummary(version) {
  const rows = summaryCount(version.summary, 'total_rows', 'row_count', 'rows')
  const cols = summaryCount(version.summary, 'total_cols', 'column_count', 'columns_count')
  if (rows && cols) return `${rows} 行 / ${cols} 列`
  if (rows) return `${rows} 行`
  if (cols) return `${cols} 列`
  return '数据版本'
}

function versionHistoryCount(version) {
  if (!version) return 0
  return props.historyItems.filter(item => isHistoryItemForVersion(item, version)).length
}

function viewVersionHistory(version) {
  detailTab.value = 'history'
  historyFilter.value = isCurrentVersion(version) ? 'current' : 'all'
  nextTick(() => {
    const firstIndex = visibleHistoryItems.value.findIndex(item => isHistoryItemForVersion(item, version))
    if (firstIndex >= 0) toggleResult(firstIndex)
    else closeExpandedResult()
  })
}

function isHistoryItemForVersion(item, version) {
  if (!item) return false
  if (item.dataset_version_id && version.id) {
    return String(item.dataset_version_id) === String(version.id)
  }
  if (item.dataset_version_no && version.version_no) {
    return String(item.dataset_version_no) === String(version.version_no)
  }
  return false
}

function versionSource(version) {
  if (isInitialVersion(version)) return '初始数据'
  const job = versionSourceJobs.value[version.source_job_id]
  const methodKey = version.source_method || job?.payload?.method
  const methodLabel = methodKey ? processingMethodMap[methodKey]?.label : ''
  return methodLabel ? `${methodLabel}生成` : '数据处理生成'
}

function versionSourceTitle(version) {
  if (isInitialVersion(version)) return '最初的的数据版本，本数据集的起点：上传的第一个数据'
  return versionSource(version)
}

function versionAnalysisTitle(version) {
  const count = versionHistoryCount(version)
  return count ? `查看这个版本的 ${count} 条分析记录` : '这个版本暂无分析记录'
}

function isInitialVersion(version) {
  const job = versionSourceJobs.value[version?.source_job_id]
  return !version?.source_job_id || version.source_job_type === 'upload_ingest' || job?.job_type === 'upload_ingest'
}

function isCurrentVersion(version) {
  if (!version) return false
  return version.is_current || String(version.id) === String(props.currentDatasetVersionId)
}

function versionDisplayName(version) {
  if (version?.name) return version.name
  if (isInitialVersion(version)) return '初始版本'
  const source = versionSource(version)
  if (source && source !== '数据版本') return source.endsWith('生成') ? `${source}版本` : source
  return `版本 v${version?.version_no ?? ''}`
}

function startRenameVersion(version) {
  renamingVersionId.value = version.id
  renamingVersionName.value = versionDisplayName(version)
  nextTick(() => {
    const el = Array.isArray(versionRenameInputRef.value)
      ? versionRenameInputRef.value[0]
      : versionRenameInputRef.value
    if (el) { el.focus(); el.select() }
  })
}

function cancelRenameVersion() {
  renamingVersionId.value = null
  renamingVersionName.value = ''
}

async function commitRenameVersion(version) {
  const name = renamingVersionName.value.trim()
  const id = renamingVersionId.value
  renamingVersionId.value = null
  renamingVersionName.value = ''
  if (!name || !id) return
  try {
    await api.renameDatasetVersion(id, name)
    const v = datasetVersions.value.find(x => x.id === id)
    if (v) v.name = name
  } catch (err) {
    console.warn('重命名版本失败', err)
  }
}

async function copyVersion(version) {
  if (!version?.id) return
  pendingCopyVersion.value = version
  copyVersionName.value = ''
  nextTick(() => versionCopyInputRef.value?.focus())
}

function useOriginalVersionName() {
  if (!pendingCopyVersion.value) return
  copyVersionName.value = versionDisplayName(pendingCopyVersion.value)
  nextTick(() => {
    versionCopyInputRef.value?.focus()
    versionCopyInputRef.value?.select()
  })
}

function cancelCopyVersion() {
  pendingCopyVersion.value = null
  copyVersionName.value = ''
}

async function confirmCopyVersion() {
  const version = pendingCopyVersion.value
  const name = copyVersionName.value.trim()
  if (!version?.id || !name) return
  pendingCopyVersion.value = null
  copyVersionName.value = ''
  try {
    const result = await api.copyDatasetVersion(version.id, name)
    emit('version-copied', result)
    emit('refresh-datasets')
    await loadDatasetVersions()
  } catch (err) {
    alert(`复制版本失败：${err.message || err}`)
  }
}

async function deleteVersion(version) {
  if (!version?.id || isCurrentVersion(version)) return
  pendingDeleteVersion.value = version
}

function cancelDeleteVersion() {
  pendingDeleteVersion.value = null
}

async function confirmDeleteVersion() {
  const version = pendingDeleteVersion.value
  if (!version?.id || isCurrentVersion(version)) return
  pendingDeleteVersion.value = null
  try {
    await api.deleteDatasetVersion(version.id)
    datasetVersions.value = datasetVersions.value.filter(item => item.id !== version.id)
    if (detailTab.value === 'history') closeExpandedResult()
    emit('version-deleted')
  } catch (err) {
    alert(`删除版本失败：${err.message || err}`)
  }
}

function variableTypeLabel(variable) {
  return variable?.type || variable?.data_type || variable?.semantic_type || '-'
}

function measureLabel(variable) {
  return variable?.measure || variable?.measure_type || variable?.role || '-'
}

function valueLabelCount(variable) {
  const labels = variable?.value_labels || {}
  return Object.keys(labels).length
}

function isCurrentHistoryItem(item) {
  if (!item?.dataset_version_id && !item?.dataset_version_no) return true
  if (props.currentDatasetVersionId && item.dataset_version_id) {
    return String(item.dataset_version_id) === String(props.currentDatasetVersionId)
  }
  if (props.currentDatasetVersionNo && item.dataset_version_no) {
    return String(item.dataset_version_no) === String(props.currentDatasetVersionNo)
  }
  return true
}

async function loadDatasetVersions() {
  if (!props.currentSessionId) {
    datasetVersions.value = []
    return
  }
  versionsLoading.value = true
  try {
    const data = await api.getDatasetVersions(props.currentSessionId)
    datasetVersions.value = data.versions || []
  } catch (err) {
    datasetVersions.value = []
    console.warn('加载数据版本失败', err)
  } finally {
    versionsLoading.value = false
  }
}

async function loadDataPreview() {
  if (!props.currentSessionId) {
    previewHeaders.value = []
    previewRows.value = []
    previewError.value = ''
    return
  }
  previewLoading.value = true
  previewError.value = ''
  try {
    const data = await api.getDataPreview(props.currentSessionId, 200)
    previewHeaders.value = data.headers || []
    previewRows.value = data.rows || []
    previewError.value = ''
  } catch (err) {
    previewHeaders.value = []
    previewRows.value = []
    previewError.value = err?.message || '数据预览加载失败，请稍后重试'
    console.warn('加载数据预览失败', err)
  } finally {
    previewLoading.value = false
  }
}

function toggleSelect(sessionId) {
  const next = new Set(selectedSessionIds.value)
  if (next.has(sessionId)) {
    next.delete(sessionId)
  } else {
    next.add(sessionId)
  }
  selectedSessionIds.value = next
}

function selectAllVisible() {
  const next = new Set(selectedSessionIds.value)
  for (const ds of visibleDataSets.value) {
    next.add(ds.sessionId)
  }
  selectedSessionIds.value = next
}

function clearSelection() {
  selectedSessionIds.value = new Set()
}

function confirmBatchDelete() {
  const count = selectedSessionIds.value.size
  if (!count) return
  if (!window.confirm(`确定删除选中的 ${count} 个数据集吗？此操作不可撤销。`)) return
  executeBatchDelete()
}

async function executeBatchDelete() {
  const sessionIds = Array.from(selectedSessionIds.value)
  try {
    const data = await api.batchDeleteDatasets(sessionIds)
    const failedCount = (data.failed || []).length
    if (failedCount) {
      alert(`已删除 ${data.count || 0} 个数据集，${failedCount} 个失败`)
    }
    selectedSessionIds.value = new Set()
    // 如果删掉了当前数据集，切空
    if (props.currentSessionId && sessionIds.includes(props.currentSessionId)) {
      emit('switch-session', '')
    }
    emit('refresh-datasets')
  } catch (e) {
    alert('批量删除失败: ' + (e.message || '未知错误'))
  }
}

function openBatchMoveDialog() {
  if (!selectedSessionIds.value.size) return
  batchMoveTargetFolderId.value = null
  showBatchMoveDialog.value = true
}

async function executeBatchMove() {
  const sessionIds = Array.from(selectedSessionIds.value)
  try {
    const data = await api.batchMoveDatasetsToFolder(sessionIds, batchMoveTargetFolderId.value || null)
    const failedCount = (data.failed || []).length
    if (failedCount) {
      alert(`已移动 ${data.count || 0} 个数据集，${failedCount} 个失败`)
    }
    selectedSessionIds.value = new Set()
    showBatchMoveDialog.value = false
    emit('refresh-datasets')
  } catch (e) {
    alert('批量移动失败: ' + (e.message || '未知错误'))
  }
}

async function loadVersionSourceJobs() {
  const jobIds = [...new Set(datasetVersions.value
    .filter(version => version.source_job_id && !version.source_method)
    .map(version => version.source_job_id))]
  if (!jobIds.length) {
    versionSourceJobs.value = {}
    return
  }
  const next = { ...versionSourceJobs.value }
  const missingIds = jobIds.filter(jobId => !next[jobId])
  if (!missingIds.length) return
  const jobs = await Promise.all(missingIds.map(jobId => api.getJob(jobId).catch(() => null)))
  jobs.forEach((job, index) => {
    if (job) next[missingIds[index]] = job
  })
  versionSourceJobs.value = next
}

function formatPreviewCell(variable, cell) {
  const valueLabels = variable?.value_labels || {}
  if (!valueLabels || cell === '' || cell == null) return cell

  const direct = valueLabels[String(cell)]
  if (direct) return direct

  const numeric = Number(cell)
  if (!Number.isNaN(numeric)) {
    const numericKey = String(Number.isInteger(numeric) ? numeric : numeric)
    if (valueLabels[numericKey]) return valueLabels[numericKey]
    const floatKey = String(numeric.toFixed(1))
    if (valueLabels[floatKey]) return valueLabels[floatKey]
  }
  return cell
}

function activateVersion(version) {
  if (!version || isCurrentVersion(version)) return
  emit('activate-version', version.id)
}

function emitDsAction(eventName, sessionId) {
  emit(eventName, sessionId)
  closeMenu()
}

watch(() => props.currentSessionId, loadDatasetVersions, { immediate: true })
watch(() => props.currentDatasetVersionId, loadDatasetVersions)
watch(datasetVersions, loadVersionSourceJobs)
watch(() => props.currentSessionId, loadDataPreview, { immediate: true })
watch(() => props.currentDatasetVersionId, loadDataPreview)
watch(() => props.currentDatasetVersionId, () => {
  historyFilter.value = 'current'
})
watch(() => props.currentSessionId, () => {
  detailTab.value = 'preview'
  historyFilter.value = 'current'
  closeExpandedResult()
  showDatasetDetail.value = false
})

</script>
