#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sched_kw_wconhist.h>
#include <list.h>
#include <util.h>
#include <list_node.h>
#include <sched_util.h>
#include <stdbool.h>
#include <rate.h>
#include <sched_macros.h>



struct sched_kw_wconhist_struct {
  int         kw_size;
  list_type * rate_list;
};



/*****************************************************************/



static sched_kw_wconhist_type * sched_kw_wconhist_alloc( ) {
  sched_kw_wconhist_type * kw = malloc(sizeof *kw);
  kw->rate_list = list_alloc();
  kw->kw_size   = 11;
  return kw;
}


static void sched_kw_wconhist_add_line(sched_kw_wconhist_type * kw , const char * line) {
  int tokens;
  char **token_list;

  sched_util_parse_line(line , &tokens , &token_list , kw->kw_size , NULL);
  {
    rate_type * rate = rate_alloc_from_token_list(kw->kw_size , (const char **) token_list);
    list_append_list_owned_ref(kw->rate_list , rate , rate_free__);
  }
  sched_util_free_token_list(tokens , token_list);
  
}



/*****************************************************************/



sched_kw_wconhist_type * sched_kw_wconhist_fscanf_alloc(FILE * stream, bool * at_eof, const char * kw_name)
{
  bool   at_eokw = false;
  char * line;
  sched_kw_wconhist_type * kw = sched_kw_wconhist_alloc();

  while(!*at_eof && !at_eokw)
  {
    line = sched_util_alloc_next_entry(stream, at_eof, &at_eokw);
    if(at_eokw)
    {
      break;
    }
    else if(*at_eof)
    {
      util_abort("%s: Reached EOF before WCONHIST was finished - aborting.\n", __func__);
    }
    else
    {
      sched_kw_wconhist_add_line(kw, line);
      free(line);
    }
  }

  return kw;
}



void sched_kw_wconhist_fprintf(const sched_kw_wconhist_type *kw , FILE *stream) {
  fprintf(stream , "WCONHIST\n");
  {
    list_node_type *rate_node = list_get_head(kw->rate_list);
    while (rate_node != NULL) {
      const rate_type * rate = list_node_value_ptr(rate_node);
      rate_fprintf(rate , stream);
      rate_node = list_node_get_next(rate_node);
    }
  }
  fprintf(stream , "/\n\n");
}



void sched_kw_wconhist_free(sched_kw_wconhist_type * kw) {
  list_free(kw->rate_list);
  free(kw);
}



void sched_kw_wconhist_fwrite(const sched_kw_wconhist_type *kw , FILE *stream) {
  {
    int wconhist_lines = list_get_size(kw->rate_list);
    util_fwrite(&wconhist_lines , sizeof wconhist_lines , 1, stream , __func__);
  }
  {
    list_node_type *rate_node = list_get_head(kw->rate_list);
    while (rate_node != NULL) {
      const rate_type * rate = list_node_value_ptr(rate_node);
      rate_fwrite(rate , stream);
      rate_node = list_node_get_next(rate_node);
    }
  }
}



sched_kw_wconhist_type * sched_kw_wconhist_fread_alloc(FILE *stream) {
  sched_kw_wconhist_type *kw = sched_kw_wconhist_alloc();
  int lines , i;
  util_fread(&lines       , sizeof lines       , 1 , stream , __func__);
  for (i=0; i < lines; i++) {
    rate_type * rate = rate_fread_alloc(stream);
    list_append_list_owned_ref(kw->rate_list , rate , rate_free__);
  } 
  return kw;
}
  


hash_type * sched_kw_wconhist_rate_hash_copyc(const sched_kw_wconhist_type * kw)
{
  int size = list_get_size(kw->rate_list);
  hash_type * rate_hash = hash_alloc();

  for(int i=0; i<size; i++)
  {
    rate_type * rate_ref = list_iget_node_value_ptr(kw->rate_list, i);
    rate_type * rate_cpy = rate_copyc(rate_ref);
    hash_insert_hash_owned_ref(rate_hash, rate_get_well_ref(rate_cpy), rate_cpy, rate_free__);
  }
  return rate_hash;
}



/***********************************************************************/

KW_FSCANF_ALLOC_IMPL(wconhist)
KW_FWRITE_IMPL(wconhist)
KW_FREAD_ALLOC_IMPL(wconhist)
KW_FREE_IMPL(wconhist)
KW_FPRINTF_IMPL(wconhist)
